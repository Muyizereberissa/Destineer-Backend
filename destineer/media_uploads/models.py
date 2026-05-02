"""
Media Uploads App - Photos and Videos for Places
"""

import uuid
from django.db import models


class PlaceMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place       = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='media')
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='uploads')
    file        = models.FileField(upload_to='places/media/')
    media_type  = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    caption     = models.CharField(max_length=300, blank=True)
    is_approved = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'place_media'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.media_type} for {self.place.name} by {self.uploaded_by}'
