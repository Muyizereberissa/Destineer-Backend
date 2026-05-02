from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from places.models import Place
from places.permissions import IsAdmin
from .models import PlaceMedia
from .serializers import PlaceMediaSerializer, MediaApprovalSerializer


class PlaceMediaListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/media/places/<place_id>/     — list approved media for a place
    POST /api/media/places/<place_id>/     — authenticated users can upload
    """
    serializer_class   = PlaceMediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        place = get_object_or_404(Place, pk=self.kwargs['place_id'])
        qs = PlaceMedia.objects.filter(place=place)
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            qs = qs.filter(is_approved=True)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['place'] = get_object_or_404(Place, pk=self.kwargs['place_id'])
        return ctx


class PlaceMediaDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/media/<id>/
    DELETE /api/media/<id>/  — owner or admin
    """
    queryset           = PlaceMedia.objects.all()
    serializer_class   = PlaceMediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.uploaded_by != request.user and not request.user.is_admin:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class PendingMediaView(generics.ListAPIView):
    """GET /api/media/pending/  — admin only: list unapproved media"""
    queryset           = PlaceMedia.objects.filter(is_approved=False).select_related('place', 'uploaded_by')
    serializer_class   = PlaceMediaSerializer
    permission_classes = [IsAdmin]


class ApproveMediaView(APIView):
    """
    PATCH /api/media/<id>/approve/  — admin only: approve or reject
    Body: { "is_approved": true }
    """
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        media = get_object_or_404(PlaceMedia, pk=pk)
        serializer = MediaApprovalSerializer(media, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MyUploadsView(generics.ListAPIView):
    """GET /api/media/my-uploads/ — current user's uploads"""
    serializer_class   = PlaceMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlaceMedia.objects.filter(uploaded_by=self.request.user).select_related('place')
