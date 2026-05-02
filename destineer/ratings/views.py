from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from places.models import Place, PlaceStats
from places.permissions import IsAdmin
from .models import Rating, Comment
from .serializers import RatingSerializer, CommentSerializer


def _update_place_stats(place):
    """Recalculate and save cached rating stats."""
    agg = Rating.objects.filter(place=place).aggregate(avg=Avg('score'))
    count = Rating.objects.filter(place=place).count()
    PlaceStats.objects.update_or_create(
        place=place,
        defaults={
            'avg_rating':    round(agg['avg'] or 0, 2),
            'total_ratings': count,
        }
    )


# ─── Rating Views ──────────────────────────────────────────────────────────────

class PlaceRatingView(APIView):
    """
    GET  /api/ratings/places/<place_id>/rate/  — get current user's rating
    POST /api/ratings/places/<place_id>/rate/  — create or update rating
    Body: { "score": 4 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, place_id):
        place  = get_object_or_404(Place, pk=place_id, is_published=True)
        rating = Rating.objects.filter(place=place, user=request.user).first()
        if not rating:
            return Response({'detail': 'You have not rated this place yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RatingSerializer(rating).data)

    def post(self, request, place_id):
        place  = get_object_or_404(Place, pk=place_id, is_published=True)
        rating, created = Rating.objects.get_or_create(place=place, user=request.user)

        serializer = RatingSerializer(
            rating, data=request.data, partial=True,
            context={'request': request, 'place': place}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _update_place_stats(place)

        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=http_status)

    def delete(self, request, place_id):
        place  = get_object_or_404(Place, pk=place_id, is_published=True)
        rating = get_object_or_404(Rating, place=place, user=request.user)
        rating.delete()
        _update_place_stats(place)
        return Response({'detail': 'Rating removed.'}, status=status.HTTP_204_NO_CONTENT)


class PlaceRatingsListView(generics.ListAPIView):
    """GET /api/ratings/places/<place_id>/ratings/  — all ratings for a place"""
    serializer_class = RatingSerializer

    def get_queryset(self):
        place = get_object_or_404(Place, pk=self.kwargs['place_id'], is_published=True)
        return Rating.objects.filter(place=place).select_related('user')


# ─── Comment Views ─────────────────────────────────────────────────────────────

class PlaceCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/ratings/places/<place_id>/comments/
    POST /api/ratings/places/<place_id>/comments/
    Body: { "body": "Amazing place!" }
    """
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        place = get_object_or_404(Place, pk=self.kwargs['place_id'], is_published=True)
        return Comment.objects.filter(place=place, is_flagged=False).select_related('user')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['place'] = get_object_or_404(Place, pk=self.kwargs['place_id'])
        return ctx


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/ratings/comments/<id>/
    PUT    /api/ratings/comments/<id>/  — owner only
    DELETE /api/ratings/comments/<id>/  — owner or admin
    """
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user and not request.user.is_admin:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class FlagCommentView(APIView):
    """PATCH /api/ratings/comments/<id>/flag/  — flag a comment for review"""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_flagged = True
        comment.save()
        return Response({'detail': 'Comment flagged for review.'})


class FlaggedCommentsView(generics.ListAPIView):
    """GET /api/ratings/comments/flagged/  — admin only"""
    queryset           = Comment.objects.filter(is_flagged=True).select_related('place', 'user')
    serializer_class   = CommentSerializer
    permission_classes = [IsAdmin]


class MyRatingsView(generics.ListAPIView):
    """GET /api/ratings/my-ratings/  — current user's ratings"""
    serializer_class   = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user).select_related('place')
