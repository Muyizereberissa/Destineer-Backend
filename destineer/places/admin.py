from django.contrib import admin
from .models import Category, Place, PlaceStats


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


class PlaceStatsInline(admin.StackedInline):
    model = PlaceStats
    extra = 0


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display   = ['name', 'location', 'category', 'is_published', 'created_at']
    list_filter    = ['is_published', 'category']
    search_fields  = ['name', 'location']
    inlines        = [PlaceStatsInline]
    actions        = ['publish_places', 'unpublish_places']

    def publish_places(self, request, queryset):
        queryset.update(is_published=True)
    publish_places.short_description = 'Publish selected places'

    def unpublish_places(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_places.short_description = 'Unpublish selected places'
