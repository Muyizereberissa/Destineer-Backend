from django.urls import path
from .views import (
    LogActivityView, RecommendationsView, RefreshRecommendationsView,
    RunAITasksView, ActivityLogView,
)

urlpatterns = [
    path('activity/',                LogActivityView.as_view(),           name='log-activity'),
    path('activity/log/',            ActivityLogView.as_view(),           name='activity-log'),
    path('recommendations/',         RecommendationsView.as_view(),       name='recommendations'),
    path('recommendations/refresh/', RefreshRecommendationsView.as_view(), name='recommendations-refresh'),
    path('run-tasks/',               RunAITasksView.as_view(),            name='run-ai-tasks'),
]
