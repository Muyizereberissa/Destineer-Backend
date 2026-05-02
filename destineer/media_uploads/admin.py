from django.contrib import admin
from .models import PlaceMedia

@admin.register(PlaceMedia)
class PlaceMediaAdmin(admin.ModelAdmin):
    list_display  = ['place', 'media_type', 'uploaded_by', 'is_approved', 'uploaded_at']
    list_filter   = ['media_type', 'is_approved']
    actions       = ['approve_media']
    def approve_media(self, request, queryset):
        queryset.update(is_approved=True)
    approve_media.short_description = 'Approve selected media'
