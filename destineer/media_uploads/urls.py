from django.urls import path
from .views import (
    PlaceMediaListCreateView, PlaceMediaDetailView,
    PendingMediaView, ApproveMediaView, MyUploadsView,
)

urlpatterns = [
    path('places/<uuid:place_id>/',   PlaceMediaListCreateView.as_view(), name='place-media-list'),
    path('<uuid:pk>/',                PlaceMediaDetailView.as_view(),     name='media-detail'),
    path('pending/',                  PendingMediaView.as_view(),         name='media-pending'),
    path('<uuid:pk>/approve/',        ApproveMediaView.as_view(),         name='media-approve'),
    path('my-uploads/',              MyUploadsView.as_view(),             name='my-uploads'),
]
