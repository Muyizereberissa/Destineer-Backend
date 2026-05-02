import math
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from .models import Category, Place, PlaceStats
from .serializers import CategorySerializer, PlaceListSerializer, PlaceDetailSerializer
from .filters import PlaceFilter
from .permissions import IsAdminOrReadOnly, IsAdmin


# ─── Category Views ────────────────────────────────────────────────────────────

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/places/categories/      — list all categories
    POST /api/places/categories/      — admin only: create category
    """
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/places/categories/<id>/
    PUT    /api/places/categories/<id>/  — admin only
    DELETE /api/places/categories/<id>/  — admin only
    """
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


# ─── Place Views ───────────────────────────────────────────────────────────────

class PlaceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/places/
         Query params:
           location=Kigali
           category=<uuid>
           category_slug=nature
           min_rating=3.5
           is_hidden_gem=true
           search=<text>                 (searches name, description, location)
           ordering=trending_score       (or avg_rating, -created_at, total_views)
    POST /api/places/  — admin only
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_class    = PlaceFilter
    search_fields      = ['name', 'description', 'location']
    ordering_fields    = ['created_at', 'stats__avg_rating', 'stats__trending_score', 'stats__total_views']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Place.objects.select_related('category', 'stats', 'created_by').prefetch_related('media')
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlaceDetailSerializer
        return PlaceListSerializer


class PlaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/places/<id>/
    PUT    /api/places/<id>/  — admin only
    DELETE /api/places/<id>/  — admin only
    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class   = PlaceDetailSerializer

    def get_queryset(self):
        qs = Place.objects.select_related('category', 'stats', 'created_by').prefetch_related('media')
        if not (self.request.user.is_authenticated and self.request.user.is_admin):
            qs = qs.filter(is_published=True)
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        PlaceStats.objects.filter(place=instance).update(total_views=F('total_views') + 1)
        # Log user activity for AI
        self._log_activity(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _log_activity(self, request, place):
        try:
            from ai_engine.models import UserActivity
            UserActivity.objects.create(
                user=request.user if request.user.is_authenticated else None,
                place=place,
                action='view',
                session_key=request.session.session_key or '',
            )
        except Exception:
            pass


# ─── Special Filtered Endpoints ────────────────────────────────────────────────

class TrendingPlacesView(generics.ListAPIView):
    """GET /api/places/trending/ — top 20 by trending score"""
    serializer_class = PlaceListSerializer

    def get_queryset(self):
        return (Place.objects
                .filter(is_published=True)
                .select_related('category', 'stats')
                .prefetch_related('media')
                .order_by('-stats__trending_score')[:20])


class TopRatedPlacesView(generics.ListAPIView):
    """GET /api/places/top-rated/ — places with highest avg_rating (min 3 ratings)"""
    serializer_class = PlaceListSerializer

    def get_queryset(self):
        return (Place.objects
                .filter(is_published=True, stats__total_ratings__gte=3)
                .select_related('category', 'stats')
                .prefetch_related('media')
                .order_by('-stats__avg_rating')[:20])


class HiddenGemsView(generics.ListAPIView):
    """GET /api/places/hidden-gems/ — high rated but low view count"""
    serializer_class = PlaceListSerializer

    def get_queryset(self):
        return (Place.objects
                .filter(is_published=True, stats__is_hidden_gem=True)
                .select_related('category', 'stats')
                .prefetch_related('media')
                .order_by('-stats__avg_rating'))


class NearbyPlacesView(APIView):
    """
    GET /api/places/nearby/?lat=-1.9441&lng=30.0619&radius=20
    Returns published places within radius km (default 20).
    """
    def get(self, request):
        try:
            lat    = float(request.query_params.get('lat', 0))
            lng    = float(request.query_params.get('lng', 0))
            radius = float(request.query_params.get('radius', 20))
        except (ValueError, TypeError):
            return Response({'detail': 'Invalid lat/lng parameters.'}, status=400)

        places   = Place.objects.filter(is_published=True, latitude__isnull=False, longitude__isnull=False)
        nearby   = []

        for place in places:
            dist = self._haversine(lat, lng, float(place.latitude), float(place.longitude))
            if dist <= radius:
                nearby.append((dist, place))

        nearby.sort(key=lambda x: x[0])
        results = [p for _, p in nearby[:30]]
        serializer = PlaceListSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))


# ─── Admin-only Stats ──────────────────────────────────────────────────────────

class AdminStatsView(APIView):
    """GET /api/places/admin/stats/ — dashboard overview"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from ratings.models import Rating, Comment
        from media_uploads.models import PlaceMedia
        from users.models import User
        return Response({
            'total_places':        Place.objects.count(),
            'published_places':    Place.objects.filter(is_published=True).count(),
            'total_users':         User.objects.filter(role='tourist').count(),
            'total_ratings':       Rating.objects.count(),
            'total_comments':      Comment.objects.count(),
            'pending_media':       PlaceMedia.objects.filter(is_approved=False).count(),
            'hidden_gems':         PlaceStats.objects.filter(is_hidden_gem=True).count(),
        })
