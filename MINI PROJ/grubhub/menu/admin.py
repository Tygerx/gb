from django.contrib import admin
from .models import MenuItem, Cart

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'availability', 'inventory', 'rating')
    list_filter = ('category', 'availability')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    list_editable = ('price', 'availability', 'inventory', 'rating')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'total_price')
    list_filter = ('user', 'item')
    search_fields = ('user__username', 'item__name')

admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Cart, CartAdmin)
