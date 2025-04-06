from menu.models import MenuItem

items = [
    {"name": "Classic Burger", "price": 149.00, "availability": True, "image": "menu_images/classic_burger.jpg"},
    {"name": "French Fries", "price": 89.00, "availability": True, "image": "menu_images/french_fries.jpg"},
    {"name": "Chocolate Shake", "price": 119.00, "availability": True, "image": "menu_images/chocolate_shake.jpg"},
]

for item in items:
    MenuItem.objects.create(
        name=item["name"],
        price=item["price"],
        availability=item["availability"],
        image=item["image"]
    )

    