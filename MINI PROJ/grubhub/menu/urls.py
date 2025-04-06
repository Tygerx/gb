from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin/', views.admin_view, name='admin'),
    path('menu/', views.menu_list, name='menu_list'),
    path('item/<int:item_id>/', views.menu_detail, name='menu_detail'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('order/', views.order, name='order'),    
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('x/', views.x_page, name='x_page'),
    path('logout/', views.logout_view, name='logout'),
    path('webhook/', views.webhook, name='webhook'),
]

