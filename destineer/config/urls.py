"""
Rwanda Tourism Explorer - Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/auth/',        include('users.urls')),
    path('api/places/',      include('places.urls')),
    path('api/media/',       include('media_uploads.urls')),
    path('api/ratings/',     include('ratings.urls')),
    path('api/ai/',          include('ai_engine.urls')),

    # API Schema & Docs
    path('api/schema/',      SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',        SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',       SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)