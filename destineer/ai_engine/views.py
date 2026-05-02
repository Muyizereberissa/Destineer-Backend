from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from places.permissions import IsAdmin
from .models import UserActivity, AIRecommendation
from .serializers import UserActivitySerializer, AIRecommendationSerializer
from .services import generate_recommendations_for_user, run_all_ai_tasks


class LogActivityView(generics.CreateAPIView):
    """
    POST /api/ai/activity/
    Body: { "place": "<uuid>", "action": "view" }
    Actions: view | rate | comment | upload
    """
    serializer_class   = UserActivitySerializer
    permission_classes = [permissions.AllowAny]


class RecommendationsView(APIView):
    """
    GET /api/ai/recommendations/
    Returns personalized recommendations for the logged-in user.
    Generates fresh ones if none exist.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        recs = AIRecommendation.objects.filter(user=request.user).select_related('place', 'place__category', 'place__stats')

        if not recs.exists():
            # Generate on-the-fly if none cached
            generate_recommendations_for_user(request.user)
            recs = AIRecommendation.objects.filter(user=request.user).select_related('place', 'place__category', 'place__stats')

        serializer = AIRecommendationSerializer(recs, many=True, context={'request': request})
        return Response(serializer.data)


class RefreshRecommendationsView(APIView):
    """
    POST /api/ai/recommendations/refresh/
    Force-regenerate recommendations for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        generate_recommendations_for_user(request.user)
        recs = AIRecommendation.objects.filter(user=request.user).select_related('place', 'place__category', 'place__stats')
        serializer = AIRecommendationSerializer(recs, many=True, context={'request': request})
        return Response({'recommendations': serializer.data, 'detail': 'Recommendations refreshed.'})


class RunAITasksView(APIView):
    """
    POST /api/ai/run-tasks/  — admin only
    Triggers trending score update + hidden gem detection.
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        result = run_all_ai_tasks()
        return Response({'detail': 'AI tasks completed.', 'results': result})


class ActivityLogView(generics.ListAPIView):
    """
    GET /api/ai/activity/log/  — admin only: view all activities
    Query params: place=<uuid>, action=view|rate|comment|upload
    """
    serializer_class   = UserActivitySerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = UserActivity.objects.select_related('user', 'place')
        place  = self.request.query_params.get('place')
        action = self.request.query_params.get('action')
        if place:
            qs = qs.filter(place_id=place)
        if action:
            qs = qs.filter(action=action)
        return qs
