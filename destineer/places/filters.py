import django_filters
from .models import Place


class PlaceFilter(django_filters.FilterSet):
    location    = django_filters.CharFilter(lookup_expr='icontains')
    category    = django_filters.UUIDFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    min_rating  = django_filters.NumberFilter(field_name='stats__avg_rating', lookup_expr='gte')
    max_rating  = django_filters.NumberFilter(field_name='stats__avg_rating', lookup_expr='lte')
    is_hidden_gem = django_filters.BooleanFilter(field_name='stats__is_hidden_gem')

    class Meta:
        model  = Place
        fields = ['location', 'category', 'category_slug', 'min_rating', 'max_rating', 'is_hidden_gem']
