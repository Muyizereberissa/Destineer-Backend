from rest_framework import serializers
from .models import PlaceMedia


class PlaceMediaSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    file_url    = serializers.SerializerMethodField()

    class Meta:
        model  = PlaceMedia
        fields = ['id', 'place', 'uploaded_by', 'file', 'file_url', 'media_type', 'caption', 'is_approved', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'is_approved', 'uploaded_at']
        extra_kwargs = {'file': {'write_only': True}, 'place': {'read_only': True}}

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        validated_data['place']       = self.context['place']

        # Auto-approve if uploader is admin
        if validated_data['uploaded_by'].is_admin:
            validated_data['is_approved'] = True

        media = super().create(validated_data)

        # Log activity
        try:
            from ai_engine.models import UserActivity
            UserActivity.objects.create(
                user=validated_data['uploaded_by'],
                place=validated_data['place'],
                action='upload',
            )
        except Exception:
            pass

        return media


class MediaApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PlaceMedia
        fields = ['id', 'is_approved']
