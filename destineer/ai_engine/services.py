import json
from google import genai
from groq import Groq
from django.conf import settings

# Configure Gemini (new way)
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Configure Groq
groq_client = Groq(api_key=settings.GROQ_API_KEY)


def analyze_place_with_gemini(place_name, description):
    """
    Use Gemini to generate rich descriptions and tags for a place.
    Called when a new place is added to the platform.
    """
    prompt = f"""
    You are an expert Rwanda tourism guide called "Destineer AI".
    
    Analyze this tourist location:
    Name: {place_name}
    Description: {description}
    
    Return a JSON response with:
    - enhanced_description: a vivid, engaging 2-sentence description
    - tags: list of 5 relevant tags (e.g. "nature", "hidden gem", "family-friendly")
    - best_time_to_visit: short recommendation
    - vibe: one word (e.g. "adventurous", "peaceful", "cultural")
    - hidden_gem_score: 1-10 (10 = very undiscovered)
    
    Only return valid JSON, no extra text.
    """

    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    return response.text


def analyze_uploaded_photo(image_path, place_name):
    """
    Use Gemini Vision to read tourist photos and describe what it sees.
    Called when a user uploads a photo of a place.
    """
    import PIL.Image
    image = PIL.Image.open(image_path)

    prompt = f"""
    This is a photo from {place_name} in Rwanda.
    In 2 sentences, describe what you see in this image for a tourism platform.
    Focus on what makes this place beautiful or interesting.
    """

    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, image],
    )
    return response.text


def get_travel_recommendations(user_interests, visited_places):
    """
    Use Groq for fast real-time recommendations.
    Called for quick chat-based suggestions.
    """
    prompt = f"""
    You are Destineer, a friendly AI travel guide for Rwanda.
    
    User interests: {user_interests}
    Places they have already visited: {visited_places}
    
    Recommend 3 places in Rwanda they haven't seen yet.
    Be specific, friendly, and enthusiastic.
    Keep response under 150 words.
    """

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content


def generate_recommendations_for_user(user):
    """
    Generate and save personalized place recommendations for a user.
    Called by RecommendationsView and RefreshRecommendationsView.
    The AI receives real user data and decides everything itself.
    """
    try:
        from .models import UserActivity, AIRecommendation
        from places.models import Place

        activity = UserActivity.objects.filter(user=user).select_related('place', 'place__category')

        visited_places = [
            {
                "name": a.place.name,
                "category": a.place.category.name if a.place.category else "unknown",
                "action": a.action,
            }
            for a in activity if a.place
        ]

        all_places = list(Place.objects.values('name', 'description'))

        prompt = f"""
        You are Destineer AI, a smart Rwanda tourism recommendation engine.

        This user's activity history:
        {json.dumps(visited_places, indent=2)}

        All available places on the platform:
        {json.dumps(all_places, indent=2)}

        Based on the user's interests and behavior patterns, recommend 3 places 
        they have NOT interacted with yet that they would genuinely love.
        
        Think carefully about patterns in what they like before deciding.

        Return ONLY a valid JSON array, nothing else:
        [
            {{"name": "exact place name from the list", "reason": "personalized one sentence reason"}},
            {{"name": "exact place name from the list", "reason": "personalized one sentence reason"}},
            {{"name": "exact place name from the list", "reason": "personalized one sentence reason"}}
        ]
        """

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()
        recommendations = json.loads(raw)

        AIRecommendation.objects.filter(user=user).delete()

        for rec in recommendations:
            place = Place.objects.filter(name__icontains=rec.get('name', '')).first()
            if place:
                AIRecommendation.objects.create(
                    user=user,
                    place=place,
                    reason=rec.get('reason', ''),
                    score=0.9,
                )

    except Exception as e:
        print(f"[Destineer AI] generate_recommendations_for_user error: {e}")


def run_all_ai_tasks():
    """
    Run all background AI tasks.
    The AI receives real platform data and decides everything:
    - Which places are hidden gems
    - Which places are trending
    - Which places are top rated
    Called by RunAITasksView (admin only).
    """
    results = {}

    try:
        from places.models import Place

        places = Place.objects.select_related('stats').all()
        places_data = [
            {
                "name": place.name,
                "description": place.description,
                "visit_count": place.stats.view_count if hasattr(place, 'stats') and place.stats else 0,
                "avg_rating": float(place.stats.average_rating) if hasattr(place, 'stats') and place.stats else 0.0,
                "total_ratings": place.stats.rating_count if hasattr(place, 'stats') and place.stats else 0,
            }
            for place in places
        ]

        prompt = f"""
        You are Destineer AI, analyzing Rwanda tourism data for a platform.

        Here is real data for all places on the platform:
        {json.dumps(places_data, indent=2)}

        Analyze this data intelligently and return a JSON object with:
        {{
            "hidden_gems": ["place names that have high ratings but very few visitors"],
            "trending": ["place names that are getting the most visits recently"],
            "top_rated": ["place names with the highest average ratings"]
        }}

        Use your judgment to decide what qualifies as a hidden gem vs trending.
        Only return the JSON object, nothing else.
        """

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()
        ai_analysis = json.loads(raw)

        Place.objects.all().update(is_hidden_gem=False)
        for name in ai_analysis.get('hidden_gems', []):
            Place.objects.filter(name__icontains=name).update(is_hidden_gem=True)

        results['hidden_gems'] = ai_analysis.get('hidden_gems', [])
        results['trending'] = ai_analysis.get('trending', [])
        results['top_rated'] = ai_analysis.get('top_rated', [])
        results['status'] = 'completed'

    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
        print(f"[Destineer AI] run_all_ai_tasks error: {e}")

    return results