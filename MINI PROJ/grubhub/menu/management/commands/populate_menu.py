from django.core.management.base import BaseCommand
from menu.models import MenuItem
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the menu with initial items'

    def handle(self, *args, **kwargs):
        # Clear existing menu items
        MenuItem.objects.all().delete()

        # Define menu items
        menu_items = [
            {
                'name': 'Margherita Pizza',
                'description': 'Classic tomato sauce with mozzarella and basil',
                'price': 299,
                'category': 'Pizza',
                'availability': True,
                'image': 'menu_images/pizza.jpg'
            },
            {
                'name': 'Pepperoni Pizza',
                'description': 'Spicy pepperoni with tomato sauce and cheese',
                'price': 399,
                'category': 'Pizza',
                'availability': True,
                'image': 'menu_images/pepperoni.jpg'
            },
            {
                'name': 'Chicken Burger',
                'description': 'Grilled chicken patty with lettuce and special sauce',
                'price': 199,
                'category': 'Burgers',
                'availability': True,
                'image': 'menu_images/burger.jpg'
            },
            {
                'name': 'Veg Burger',
                'description': 'Vegetable patty with fresh vegetables',
                'price': 179,
                'category': 'Burgers',
                'availability': True,
                'image': 'menu_images/veg-burger.jpg'
            },
            {
                'name': 'Pasta Alfredo',
                'description': 'Creamy Alfredo sauce with fettuccine',
                'price': 249,
                'category': 'Pasta',
                'availability': True,
                'image': 'menu_images/pasta.jpg'
            },
            {
                'name': 'Spaghetti',
                'description': 'Classic tomato sauce with spaghetti',
                'price': 229,
                'category': 'Pasta',
                'availability': True,
                'image': 'menu_images/spaghetti.jpg'
            }
        ]

        # Create menu items
        for item_data in menu_items:
            # Check if image exists
            image_path = os.path.join(settings.MEDIA_ROOT, item_data['image'])
            if not os.path.exists(image_path):
                self.stdout.write(self.style.WARNING(f"Warning: Image not found for {item_data['name']}"))
                item_data['image'] = None

            MenuItem.objects.create(**item_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated menu items'))