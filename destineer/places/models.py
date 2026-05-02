"""
Places App - Destinations, Categories, Stats
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon name or emoji')

    class Meta:
        db_table  = 'categories'
        ordering  = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Place(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name           = models.CharField(max_length=200)
    description    = models.TextField()
    location       = models.CharField(max_length=200, help_text='City or district name')
    latitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_map_link = models.URLField(blank=True)
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='places')
    created_by     = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_places')
    is_published   = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'places'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PlaceStats(models.Model):
    """Cached statistics computed by the AI engine."""
    place          = models.OneToOneField(Place, on_delete=models.CASCADE, related_name='stats', primary_key=True)
    avg_rating     = models.FloatField(default=0.0)
    total_ratings  = models.IntegerField(default=0)
    total_views    = models.IntegerField(default=0)
    trending_score = models.FloatField(default=0.0)
    is_hidden_gem  = models.BooleanField(default=False)
    last_updated   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'place_stats'

    def __str__(self):
        return f'Stats for {self.place.name}'
