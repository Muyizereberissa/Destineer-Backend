"""
Management command to seed the database with sample Rwanda tourism data.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from users.models import User
from places.models import Category, Place, PlaceStats


CATEGORIES = [
    {'name': 'Nature & Wildlife', 'icon': '🦍'},
    {'name': 'Culture & Heritage', 'icon': '🏛️'},
    {'name': 'Adventure',         'icon': '🧗'},
    {'name': 'Food & Dining',     'icon': '🍽️'},
    {'name': 'Lakes & Beaches',   'icon': '🏖️'},
    {'name': 'Volcanoes',         'icon': '🌋'},
]

PLACES = [
    {
        'name': 'Volcanoes National Park',
        'description': 'Home to the endangered mountain gorillas, Volcanoes National Park is one of Africa\'s most prestigious wildlife destinations. Visitors can trek through misty bamboo forests to encounter gorilla families in their natural habitat.',
        'location': 'Musanze, Northern Province',
        'latitude': -1.4833, 'longitude': 29.6333,
        'google_map_link': 'https://maps.google.com/?q=Volcanoes+National+Park+Rwanda',
        'category': 'Volcanoes',
        'avg_rating': 4.9, 'total_ratings': 312, 'total_views': 4500,
    },
    {
        'name': 'Lake Kivu',
        'description': 'One of Africa\'s Great Lakes, Lake Kivu stretches along Rwanda\'s western border with the DRC. The lake offers stunning sunsets, boat rides to volcanic islands, and a relaxing beach scene in Gisenyi and Kibuye.',
        'location': 'Rubavu, Western Province',
        'latitude': -2.0667, 'longitude': 29.2333,
        'google_map_link': 'https://maps.google.com/?q=Lake+Kivu+Rwanda',
        'category': 'Lakes & Beaches',
        'avg_rating': 4.7, 'total_ratings': 198, 'total_views': 3100,
    },
    {
        'name': 'Kigali Genocide Memorial',
        'description': 'A deeply moving site that serves as the final resting place for more than 250,000 genocide victims. The memorial educates visitors about the 1994 genocide against the Tutsi and honours those who perished.',
        'location': 'Kigali',
        'latitude': -1.9536, 'longitude': 30.0613,
        'google_map_link': 'https://maps.google.com/?q=Kigali+Genocide+Memorial',
        'category': 'Culture & Heritage',
        'avg_rating': 4.8, 'total_ratings': 425, 'total_views': 6200,
    },
    {
        'name': 'Nyungwe Forest National Park',
        'description': 'One of Africa\'s oldest rainforests, Nyungwe offers chimpanzee trekking, a thrilling canopy walkway, and incredible birdwatching with over 300 species. The forest covers 1,013 km² of pristine jungle.',
        'location': 'Nyamasheke, Western Province',
        'latitude': -2.4833, 'longitude': 29.1833,
        'google_map_link': 'https://maps.google.com/?q=Nyungwe+Forest+National+Park',
        'category': 'Nature & Wildlife',
        'avg_rating': 4.6, 'total_ratings': 156, 'total_views': 2800,
    },
    {
        'name': 'Akagera National Park',
        'description': 'Rwanda\'s only savannah park, Akagera is home to the Big Five — lion, leopard, elephant, buffalo, and rhino. The park also features lakes, papyrus swamps, and a growing population of reintroduced lions and rhinos.',
        'location': 'Eastern Province',
        'latitude': -1.9167, 'longitude': 30.7167,
        'google_map_link': 'https://maps.google.com/?q=Akagera+National+Park+Rwanda',
        'category': 'Nature & Wildlife',
        'avg_rating': 4.5, 'total_ratings': 134, 'total_views': 2200,
    },
    {
        'name': 'Inema Arts Center',
        'description': 'A vibrant creative hub in Kigali showcasing contemporary Rwandan art. The center hosts regular exhibitions, live music, and dance performances, offering visitors a window into Rwanda\'s thriving modern arts scene.',
        'location': 'Kigali, Kimihurura',
        'latitude': -1.9441, 'longitude': 30.0900,
        'google_map_link': 'https://maps.google.com/?q=Inema+Arts+Center+Kigali',
        'category': 'Culture & Heritage',
        'avg_rating': 4.3, 'total_ratings': 87, 'total_views': 890,
        'is_hidden_gem': True,
    },
    {
        'name': 'Twin Lakes (Burera & Ruhondo)',
        'description': 'Two stunningly beautiful volcanic lakes in northern Rwanda, surrounded by steep hills and traditional villages. Rarely visited by tourists, they offer breathtaking scenery and authentic local culture.',
        'location': 'Burera, Northern Province',
        'latitude': -1.4500, 'longitude': 29.8167,
        'google_map_link': 'https://maps.google.com/?q=Lake+Burera+Rwanda',
        'category': 'Lakes & Beaches',
        'avg_rating': 4.7, 'total_ratings': 42, 'total_views': 380,
        'is_hidden_gem': True,
    },
    {
        'name': 'Musanze Caves',
        'description': 'Ancient lava tube caves stretching over 2 km near Musanze town. The caves were historically used as refuge during inter-clan wars and offer a fascinating underground exploration experience.',
        'location': 'Musanze, Northern Province',
        'latitude': -1.5000, 'longitude': 29.6333,
        'google_map_link': 'https://maps.google.com/?q=Musanze+Caves+Rwanda',
        'category': 'Adventure',
        'avg_rating': 4.2, 'total_ratings': 63, 'total_views': 720,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample Rwanda tourism data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌍 Seeding Rwanda Tourism data...\n')

        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@visitrwanda.rw',
            defaults={'name': 'Admin User', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('Admin@1234')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created: admin@visitrwanda.rw / Admin@1234'))
        else:
            self.stdout.write('  → Admin user already exists')

        # Create tourist user
        tourist, created = User.objects.get_or_create(
            email='tourist@example.com',
            defaults={'name': 'Test Tourist', 'role': 'tourist'}
        )
        if created:
            tourist.set_password('Tourist@1234')
            tourist.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Tourist user created: tourist@example.com / Tourist@1234'))

        # Create categories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': slugify(cat_data['name']), 'icon': cat_data['icon']}
            )
            cat_map[cat_data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Category: {cat.name}'))

        # Create places
        for p in PLACES:
            cat    = cat_map.get(p.pop('category'))
            rating = p.pop('avg_rating')
            total_r = p.pop('total_ratings')
            total_v = p.pop('total_views')
            is_gem  = p.pop('is_hidden_gem', False)

            place, created = Place.objects.get_or_create(
                name=p['name'],
                defaults={**p, 'category': cat, 'created_by': admin, 'is_published': True}
            )
            if created:
                PlaceStats.objects.update_or_create(
                    place=place,
                    defaults={
                        'avg_rating': rating, 'total_ratings': total_r,
                        'total_views': total_v, 'is_hidden_gem': is_gem,
                        'trending_score': round((total_v * 0.4 + total_r * 0.3), 2),
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Place: {place.name}'))
            else:
                self.stdout.write(f'  → Place already exists: {place.name}')

        self.stdout.write('\n' + self.style.SUCCESS('✅ Seeding complete!'))
        self.stdout.write('\nTest credentials:')
        self.stdout.write('  Admin:   admin@visitrwanda.rw  / Admin@1234')
        self.stdout.write('  Tourist: tourist@example.com   / Tourist@1234')
