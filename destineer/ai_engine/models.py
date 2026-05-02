"""
AI Engine App - Activity Tracking and Recommendations
"""

import uuid
from django.db import models


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('view',    'View'),
        ('rate',    'Rate'),
        ('comment', 'Comment'),
        ('upload',  'Upload'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    place       = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='activities')
    action      = models.CharField(max_length=10, choices=ACTION_CHOICES)
    session_key = models.CharField(max_length=100, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
        indexes  = [
            models.Index(fields=['place', 'action', 'timestamp']),
            models.Index(fields=['user', 'action']),
        ]

    def __str__(self):
        actor = self.user.name if self.user else 'Anonymous'
        return f'{actor} {self.action}d {self.place.name}'


class AIRecommendation(models.Model):
    REASON_CHOICES = [
        ('trending',      'Trending'),
        ('nearby',        'Nearby'),
        ('similar_taste', 'Similar Taste'),
        ('top_rated',     'Top Rated'),
        ('hidden_gem',    'Hidden Gem'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user         = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recommendations')
    place        = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='recommended_to')
    score        = models.FloatField(default=0.0)
    reason       = models.CharField(max_length=20, choices=REASON_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'ai_recommendations'
        ordering        = ['-score']
        unique_together = ('user', 'place')

    def __str__(self):
        return f'Recommend {self.place.name} to {self.user.name} ({self.reason})'
