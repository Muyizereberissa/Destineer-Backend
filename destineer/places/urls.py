from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    PlaceListCreateView, PlaceDetailView,
    TrendingPlacesView, TopRatedPlacesView, HiddenGemsView, NearbyPlacesView,
    AdminStatsView,
)

urlpatterns = [
    # Categories
    path('categories/',         CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(),   name='category-detail'),

    # Special place feeds (must come before <uuid:pk>)
    path('trending/',           TrendingPlacesView.as_view(),     name='place-trending'),
    path('top-rated/',          TopRatedPlacesView.as_view(),     name='place-top-rated'),
    path('hidden-gems/',        HiddenGemsView.as_view(),         name='place-hidden-gems'),
    path('nearby/',             NearbyPlacesView.as_view(),       name='place-nearby'),
    path('admin/stats/',        AdminStatsView.as_view(),         name='admin-stats'),

    # CRUD
    path('',                    PlaceListCreateView.as_view(),    name='place-list'),
    path('<uuid:pk>/',          PlaceDetailView.as_view(),        name='place-detail'),
]
