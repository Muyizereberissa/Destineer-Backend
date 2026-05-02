from rest_framework import serializers
from .models import UserActivity, AIRecommendation
from places.serializers import PlaceListSerializer


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserActivity
        fields = ['id', 'place', 'action', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user']        = request.user if request.user.is_authenticated else None
        validated_data['session_key'] = request.session.session_key or ''
        return super().create(validated_data)


class AIRecommendationSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)

    class Meta:
        model  = AIRecommendation
        fields = ['id', 'place', 'score', 'reason', 'generated_at']
