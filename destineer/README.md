# 🌍 Rwanda Tourism Explorer — Django Backend

Community-driven travel guide for Rwanda destinations. Built with Django REST Framework.

---

## 🚀 Quick Start (5 minutes)

### Option A — Automated Setup (recommended)
```bash
cd rwanda_tourism
bash setup.sh
python manage.py runserver
```

### Option B — Manual Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env           # Edit .env with your settings

# 4. For quick testing — switch to SQLite in config/settings.py:
#    Uncomment the SQLite DATABASES block and comment out PostgreSQL

# 5. Run migrations
python manage.py makemigrations users places media_uploads ratings ai_engine
python manage.py migrate

# 6. Seed sample data (8 Rwanda places + test users)
python manage.py seed_data

# 7. Start server
python manage.py runserver
```

---

## 🧪 Test with Postman

1. Open Postman → **Import** → select `Rwanda_Tourism_API.postman_collection.json`
2. The collection variable `base_url` is pre-set to `http://127.0.0.1:8000`
3. Run **"Login (saves token automatically)"** — the token auto-saves to `{{token}}`
4. All protected requests automatically use `Bearer {{token}}`

### Test Users (created by seed_data)
| Role    | Email                    | Password      |
|---------|--------------------------|---------------|
| Admin   | admin@visitrwanda.rw     | Admin@1234    |
| Tourist | tourist@example.com      | Tourist@1234  |

---

## 📡 API Endpoints

### Auth  `/api/auth/`
| Method | Endpoint              | Auth     | Description                  |
|--------|-----------------------|----------|------------------------------|
| POST   | `/register/`          | Public   | Register new user            |
| POST   | `/login/`             | Public   | Login, returns JWT tokens    |
| POST   | `/logout/`            | Required | Blacklist refresh token      |
| POST   | `/token/refresh/`     | Public   | Refresh access token         |
| GET    | `/profile/`           | Required | Get current user profile     |
| PATCH  | `/profile/`           | Required | Update profile               |
| POST   | `/change-password/`   | Required | Change password              |
| GET    | `/users/`             | Admin    | List all users               |

### Places  `/api/places/`
| Method | Endpoint              | Auth     | Description                  |
|--------|-----------------------|----------|------------------------------|
| GET    | `/`                   | Public   | List places (with filters)   |
| POST   | `/`                   | Admin    | Create a place               |
| GET    | `/<id>/`              | Public   | Place detail + increments view|
| PATCH  | `/<id>/`              | Admin    | Update place                 |
| DELETE | `/<id>/`              | Admin    | Delete place                 |
| GET    | `/trending/`          | Public   | Top 20 by trending score     |
| GET    | `/top-rated/`         | Public   | Highest rated (min 3 ratings)|
| GET    | `/hidden-gems/`       | Public   | AI-flagged hidden gems       |
| GET    | `/nearby/?lat=&lng=`  | Public   | Places within radius (km)    |
| GET    | `/admin/stats/`       | Admin    | Dashboard overview           |

**Place Filters:**
```
?location=Kigali
?category=<uuid>
?category_slug=nature-wildlife
?min_rating=4.0
?is_hidden_gem=true
?search=gorilla
?ordering=-stats__trending_score   (or avg_rating, total_views, created_at)
```

### Categories  `/api/places/categories/`
| Method | Endpoint   | Auth   | Description       |
|--------|------------|--------|-------------------|
| GET    | `/`        | Public | List categories   |
| POST   | `/`        | Admin  | Create category   |
| GET    | `/<id>/`   | Public | Category detail   |
| PATCH  | `/<id>/`   | Admin  | Update category   |
| DELETE | `/<id>/`   | Admin  | Delete category   |

### Media  `/api/media/`
| Method | Endpoint                   | Auth     | Description               |
|--------|----------------------------|----------|---------------------------|
| GET    | `/places/<place_id>/`      | Public   | List approved media       |
| POST   | `/places/<place_id>/`      | Required | Upload image/video        |
| GET    | `/<id>/`                   | Public   | Media detail              |
| DELETE | `/<id>/`                   | Owner/Admin | Delete media           |
| GET    | `/pending/`                | Admin    | Unapproved uploads        |
| PATCH  | `/<id>/approve/`           | Admin    | Approve/reject media      |
| GET    | `/my-uploads/`             | Required | My uploaded media         |

### Ratings & Comments  `/api/ratings/`
| Method | Endpoint                       | Auth     | Description             |
|--------|--------------------------------|----------|-------------------------|
| POST   | `/places/<id>/rate/`           | Required | Rate a place (1-5)      |
| GET    | `/places/<id>/rate/`           | Required | Get my rating           |
| DELETE | `/places/<id>/rate/`           | Required | Remove my rating        |
| GET    | `/places/<id>/ratings/`        | Public   | All ratings for a place |
| GET    | `/my-ratings/`                 | Required | My ratings history      |
| GET    | `/places/<id>/comments/`       | Public   | List comments           |
| POST   | `/places/<id>/comments/`       | Required | Add a comment           |
| PATCH  | `/comments/<id>/`              | Owner    | Edit comment            |
| DELETE | `/comments/<id>/`              | Owner/Admin | Delete comment       |
| PATCH  | `/comments/<id>/flag/`         | Required | Flag for review         |
| GET    | `/comments/flagged/`           | Admin    | Flagged comments        |

### AI Engine  `/api/ai/`
| Method | Endpoint                    | Auth     | Description                    |
|--------|-----------------------------|----------|--------------------------------|
| POST   | `/activity/`                | Public   | Log user activity              |
| GET    | `/activity/log/`            | Admin    | Full activity log              |
| GET    | `/recommendations/`         | Required | Personalized recommendations   |
| POST   | `/recommendations/refresh/` | Required | Force regenerate               |
| POST   | `/run-tasks/`               | Admin    | Update trending + hidden gems  |

---

## 🗄️ Database Schema

```
users           → id, name, email, role, profile_picture, bio
categories      → id, name, slug, icon
places          → id, name, description, location, lat, lng, category, is_published
place_stats     → place, avg_rating, total_ratings, total_views, trending_score, is_hidden_gem
place_media     → id, place, uploaded_by, file, media_type, caption, is_approved
ratings         → id, place, user, score   [unique: place+user]
comments        → id, place, user, body, is_flagged
user_activities → id, user, place, action, session_key, timestamp
ai_recommendations → id, user, place, score, reason
```

---

## 🤖 AI Logic

**Trending Score** (updates hourly via `/api/ai/run-tasks/`):
```
score = (views × 0.4) + (ratings × 0.3) + (comments × 0.2) + (uploads × 0.1)
window = last 7 days
```

**Hidden Gems** detection:
```
avg_rating >= 4.0 AND total_ratings >= 2 AND total_views < 50
```

**Recommendations** (per user):
- Excludes places the user already rated
- Scores by `(avg_rating/5 × 0.6) + (trending_score × 0.4)`
- Boosts hidden gems by +0.1
- Labels: `trending`, `top_rated`, `hidden_gem`, `similar_taste`

---

## 🔧 Project Structure
```
rwanda_tourism/
├── config/              # settings.py, urls.py, wsgi.py
├── users/               # Custom User model, JWT auth
├── places/              # Places, Categories, PlaceStats
│   └── management/commands/seed_data.py
├── media_uploads/       # Photo & video uploads
├── ratings/             # Ratings (1-5) + Comments
├── ai_engine/           # Activity tracking + AI scoring
├── requirements.txt
├── setup.sh
└── Rwanda_Tourism_API.postman_collection.json
```

---

## 🌐 API Docs (auto-generated)
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc:       http://127.0.0.1:8000/api/redoc/
- Django Admin: http://127.0.0.1:8000/admin/

---

## ☁️ Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure PostgreSQL credentials in `.env`
- [ ] Set up Cloudinary for media storage (uncomment in settings.py)
- [ ] Set `SECRET_KEY` to a long random string
- [ ] Add your domain to `ALLOWED_HOSTS`
- [ ] Set specific origins in `CORS_ALLOWED_ORIGINS`
- [ ] Set up Redis + Celery for background AI tasks
- [ ] Run `python manage.py collectstatic`
- [ ] Use Gunicorn: `gunicorn config.wsgi:application`
