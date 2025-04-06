from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.utils import timezone


# MenuItem Model
class MenuItem(models.Model):
    name = models.CharField(max_length=100)  # Name of the menu item
    description = models.TextField()  # Description of the item
    category = models.CharField(max_length=50)  # E.g., snacks, beverages
    image = models.ImageField(upload_to='menu/images/', null=True, blank=True)  # Upload path for menu item images
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the menu item
    availability = models.BooleanField(default=True)  # Whether the item is available
    inventory = models.IntegerField(default=0)  # Number of items in stock
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Item rating (0-5)
    allergens = models.CharField(max_length=200, default='', blank=True)  # Make allergens optional with empty default
    preparation_time = models.IntegerField(default=15)  # Default preparation time in minutes

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return static('menu/images/food-wallpaper.jpg')


# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart - {self.item.name}"

    @property
    def total_price(self):
        return self.quantity * self.item.price

    class Meta:
        unique_together = ('user', 'item')