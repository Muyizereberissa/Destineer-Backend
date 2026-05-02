from rest_framework import serializers
from .models import Rating, Comment


class RatingSerializer(serializers.ModelSerializer):
    user       = serializers.StringRelatedField(read_only=True)
    place_name = serializers.CharField(source='place.name', read_only=True)

    class Meta:
        model  = Rating
        fields = ['id', 'place', 'user', 'place_name', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'place': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user']  = self.context['request'].user
        validated_data['place'] = self.context['place']
        # Log activity
        try:
            from ai_engine.models import UserActivity
            UserActivity.objects.create(
                user=validated_data['user'],
                place=validated_data['place'],
                action='rate',
            )
        except Exception:
            pass
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        validated_data.pop('place', None)
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user      = serializers.StringRelatedField(read_only=True)
    user_id   = serializers.UUIDField(source='user.id', read_only=True)

    class Meta:
        model  = Comment
        fields = ['id', 'place', 'user', 'user_id', 'body', 'is_flagged', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_id', 'is_flagged', 'created_at', 'updated_at']
        extra_kwargs = {'place': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user']  = self.context['request'].user
        validated_data['place'] = self.context['place']
        # Log activity
        try:
            from ai_engine.models import UserActivity
            UserActivity.objects.create(
                user=validated_data['user'],
                place=validated_data['place'],
                action='comment',
            )
        except Exception:
            pass
        return super().create(validated_data)
