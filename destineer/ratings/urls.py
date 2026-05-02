from django.urls import path
from .views import (
    PlaceRatingView, PlaceRatingsListView,
    PlaceCommentListCreateView, CommentDetailView,
    FlagCommentView, FlaggedCommentsView, MyRatingsView,
)

urlpatterns = [
    # Ratings
    path('places/<uuid:place_id>/rate/',     PlaceRatingView.as_view(),            name='place-rate'),
    path('places/<uuid:place_id>/ratings/',  PlaceRatingsListView.as_view(),        name='place-ratings-list'),
    path('my-ratings/',                      MyRatingsView.as_view(),               name='my-ratings'),

    # Comments
    path('places/<uuid:place_id>/comments/', PlaceCommentListCreateView.as_view(),  name='place-comments'),
    path('comments/<uuid:pk>/',              CommentDetailView.as_view(),           name='comment-detail'),
    path('comments/<uuid:pk>/flag/',         FlagCommentView.as_view(),             name='comment-flag'),
    path('comments/flagged/',                FlaggedCommentsView.as_view(),         name='comments-flagged'),
]
