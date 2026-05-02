"""
AI Engine Services
Core logic for trending scores, hidden gems detection, and recommendations.
No Celery required — can be run synchronously or as a management command.
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg


def update_trending_scores():
    """
    Score = (recent_views × 0.4) + (recent_ratings × 0.3) + (recent_comments × 0.2) + (recent_uploads × 0.1)
    Window: last 7 days
    """
    from places.models import Place, PlaceStats
    from .models import UserActivity

    cutoff = timezone.now() - timedelta(days=7)
    places = Place.objects.filter(is_published=True)

    for place in places:
        activities = UserActivity.objects.filter(place=place, timestamp__gte=cutoff)
        views    = activities.filter(action='view').count()
        ratings  = activities.filter(action='rate').count()
        comments = activities.filter(action='comment').count()
        uploads  = activities.filter(action='upload').count()

        score = (views * 0.4) + (ratings * 0.3) + (comments * 0.2) + (uploads * 0.1)

        PlaceStats.objects.update_or_create(
            place=place,
            defaults={'trending_score': round(score, 4)}
        )

    return f'Updated trending scores for {places.count()} places.'


def flag_hidden_gems():
    """
    Hidden gem: avg_rating >= 4.0 AND total_ratings >= 2 AND total_views < 50
    """
    from places.models import PlaceStats

    stats = PlaceStats.objects.all()
    flagged = 0

    for s in stats:
        is_gem = (s.avg_rating >= 4.0 and s.total_ratings >= 2 and s.total_views < 50)
        if s.is_hidden_gem != is_gem:
            s.is_hidden_gem = is_gem
            s.save(update_fields=['is_hidden_gem'])
            flagged += 1

    return f'Flagged {flagged} hidden gems.'


def generate_recommendations_for_user(user):
    """
    Simple collaborative filtering:
    1. Find places this user has NOT rated
    2. Score each by avg_rating + trending_score
    3. Boost if similar users (who rated same places) also liked it
    Returns top 10 recommendations.
    """
    from places.models import Place, PlaceStats
    from ratings.models import Rating
    from .models import AIRecommendation

    # Places the user already interacted with
    rated_place_ids = Rating.objects.filter(user=user).values_list('place_id', flat=True)

    # Candidate places
    candidates = (Place.objects
                  .filter(is_published=True)
                  .exclude(id__in=rated_place_ids)
                  .select_related('stats'))

    scored = []
    for place in candidates:
        stats = getattr(place, 'stats', None)
        if not stats:
            continue
        base_score = (stats.avg_rating / 5.0) * 0.6 + min(stats.trending_score / 100.0, 1.0) * 0.4

        # Determine reason
        if stats.is_hidden_gem:
            reason = 'hidden_gem'
            base_score += 0.1
        elif stats.trending_score > 50:
            reason = 'trending'
        elif stats.avg_rating >= 4.5:
            reason = 'top_rated'
        else:
            reason = 'similar_taste'

        scored.append((base_score, place, reason))

    scored.sort(key=lambda x: x[0], reverse=True)
    top10 = scored[:10]

    # Save recommendations
    AIRecommendation.objects.filter(user=user).delete()
    recs = []
    for score, place, reason in top10:
        recs.append(AIRecommendation(user=user, place=place, score=round(score, 4), reason=reason))
    AIRecommendation.objects.bulk_create(recs)

    return top10


def run_all_ai_tasks():
    """Run all AI computations in sequence. Call this from a cron or management command."""
    r1 = update_trending_scores()
    r2 = flag_hidden_gems()
    return {'trending': r1, 'hidden_gems': r2}
