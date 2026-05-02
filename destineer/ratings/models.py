"""
Ratings App - Ratings and Comments
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place      = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='ratings')
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ratings')
    score      = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'ratings'
        unique_together = ('place', 'user')
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.user.name} rated {self.place.name}: {self.score}/5'


class Comment(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place      = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
    body       = models.TextField()
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.name} on {self.place.name}'
