from rest_framework import serializers
from .models import Category, Place, PlaceStats


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon']


class PlaceStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PlaceStats
        fields = ['avg_rating', 'total_ratings', 'total_views', 'trending_score', 'is_hidden_gem']


class PlaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    category     = CategorySerializer(read_only=True)
    stats        = PlaceStatsSerializer(read_only=True)
    cover_image  = serializers.SerializerMethodField()

    class Meta:
        model  = Place
        fields = [
            'id', 'name', 'location', 'category', 'stats',
            'cover_image', 'is_published', 'created_at'
        ]

    def get_cover_image(self, obj):
        media = obj.media.filter(media_type='image', is_approved=True).first()
        if media:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(media.file.url)
            return media.file.url
        return None


class PlaceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail/create/update views."""
    category     = CategorySerializer(read_only=True)
    category_id  = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    stats        = PlaceStatsSerializer(read_only=True)
    created_by   = serializers.StringRelatedField(read_only=True)
    media        = serializers.SerializerMethodField()

    class Meta:
        model  = Place
        fields = [
            'id', 'name', 'description', 'location', 'latitude', 'longitude',
            'google_map_link', 'category', 'category_id', 'created_by',
            'is_published', 'stats', 'media', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_media(self, obj):
        from media_uploads.serializers import PlaceMediaSerializer
        qs = obj.media.filter(is_approved=True)
        return PlaceMediaSerializer(qs, many=True, context=self.context).data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        place = super().create(validated_data)
        # Create empty stats record
        PlaceStats.objects.get_or_create(place=place)
        return place
