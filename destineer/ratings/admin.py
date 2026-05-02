from django.contrib import admin
from .models import Rating, Comment

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'score', 'created_at']
    list_filter  = ['score']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'is_flagged', 'created_at']
    list_filter  = ['is_flagged']
    actions      = ['unflag']
    def unflag(self, request, queryset): queryset.update(is_flagged=False)
    unflag.short_description = 'Unflag selected comments'
