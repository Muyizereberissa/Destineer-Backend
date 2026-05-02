from django.contrib import admin
from .models import UserActivity, AIRecommendation

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'action', 'timestamp']
    list_filter  = ['action']

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'reason', 'score', 'generated_at']
    list_filter  = ['reason']
