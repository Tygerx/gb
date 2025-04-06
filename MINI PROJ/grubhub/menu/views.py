from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from .models import MenuItem, Cart
import json
from django.core.management import call_command
from django.contrib import messages
import razorpay
from django.conf import settings
import time
from django.contrib.auth import logout
from django.urls import reverse

# Home Page
def home(request):
    if not request.user.is_authenticated:
        return redirect('menu:login')
    return render(request, 'menu/home.html')


# Menu List View
def menu_list(request):
    items = MenuItem.objects.all()
    for item in items:
        if not item.image:
            item.image = 'menu/images/food-wallpaper.jpg'  # Use existing image as default
    return render(request, 'menu/menu_list.html', {'items': items})


# Menu Detail View
def menu_detail(request, item_id):
    try:
        item = MenuItem.objects.get(id=item_id)
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'availability': item.availability,
            'description': item.description,
            'category': item.category,
            'allergens': item.allergens,
            'preparation_time': item.preparation_time,
            'inventory': item.inventory,
            'rating': item.rating
        })
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Menu item not found'}, status=404)


# Add to Cart
@login_required
def add_to_cart(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
    try:
        print(f"Adding item {item_id} to cart for user {request.user.username}")  # Debug print
        
        item = MenuItem.objects.get(id=item_id)
        if not item.availability:
            print(f"Item {item_id} is not available")  # Debug print
            return JsonResponse({'error': 'Item is not available'}, status=400)
        
        # Get or create cart item
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            item=item,
            defaults={'quantity': 1}
        )
        
        if not created:
            # If item already exists in cart, increment quantity
            cart_item.quantity += 1
            cart_item.save()
            print(f"Updated quantity for item {item_id} in cart")  # Debug print
        else:
            print(f"Created new cart item for {item_id}")  # Debug print
        
        # Get updated cart data
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        cart_data = []
        total = 0
        
        for cart_item in cart_items:
            item_data = {
                'id': cart_item.id,
                'item': {
                    'id': cart_item.item.id,
                    'name': cart_item.item.name,
                    'price': float(cart_item.item.price),
                    'image': cart_item.item.image.url if cart_item.item.image else None
                },
                'quantity': cart_item.quantity
            }
            cart_data.append(item_data)
            total += float(cart_item.item.price) * cart_item.quantity
        
        print(f"Cart updated successfully. Total items: {len(cart_data)}, Total amount: {total}")
        return JsonResponse({
            'message': f'{item.name} added to cart',
            'cart_items': cart_data,
            'total': float(total)
        })
    except MenuItem.DoesNotExist:
        print(f"Item {item_id} not found")  # Debug print
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)


# View Cart
@login_required
def cart(request):
    try:
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        cart_data = []
        total = 0
        
        for cart_item in cart_items:
            item_data = {
                'id': cart_item.item.id,
                'name': cart_item.item.name,
                'price': float(cart_item.item.price),
                'quantity': cart_item.quantity,
                'image': cart_item.item.image.url if cart_item.item.image else None
            }
            cart_data.append(item_data)
            total += float(cart_item.item.price) * cart_item.quantity
        
        return JsonResponse({
            'cart': cart_data,
            'total': total
        })
    except Exception as e:
        print(f"Error in cart view: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)


# Remove from Cart
@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        try:
            cart_item = Cart.objects.get(user=request.user, item_id=product_id)
            cart_item.delete()
            
            # Get updated cart data
            cart_items = Cart.objects.filter(user=request.user).select_related('item')
            cart_data = []
            total = 0
            
            for item in cart_items:
                item_data = {
                    'id': item.id,
                    'item': {
                        'id': item.item.id,
                        'name': item.item.name,
                        'price': float(item.item.price),
                        'image': item.item.image.url if item.item.image else None
                    },
                    'quantity': item.quantity
                }
                cart_data.append(item_data)
                total += float(item.item.price) * item.quantity
            
            return JsonResponse({
                'message': 'Item removed from cart',
                'cart_items': cart_data,
                'total': float(total)
            })
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)
        except Exception as e:
            print(f"Error in remove_from_cart: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Update Cart (Increment/Decrement)
@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            
            if quantity < 1:
                return JsonResponse({'error': 'Quantity cannot be less than 1'}, status=400)
            
            cart_item = Cart.objects.get(user=request.user, item_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            
            # Get updated cart data
            cart_items = Cart.objects.filter(user=request.user).select_related('item')
            cart_data = []
            total = 0
            
            for item in cart_items:
                item_data = {
                    'id': item.id,
                    'item': {
                        'id': item.item.id,
                        'name': item.item.name,
                        'price': float(item.item.price),
                        'image': item.item.image.url if item.item.image else None
                    },
                    'quantity': item.quantity
                }
                cart_data.append(item_data)
                total += float(item.item.price) * item.quantity
            
            return JsonResponse({
                'message': 'Cart updated successfully',
                'cart_items': cart_data,
                'total': float(total)
            })
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)
        except Exception as e:
            print(f"Error in update_cart: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def order(request):
    try:
        print("Order view accessed")  # Debug print
        
        # Get all menu items ordered by category and name
        menu = MenuItem.objects.all().order_by('category', 'name')
        print(f"Number of menu items: {menu.count()}")  # Debug print
        
        # Get distinct categories
        categories = MenuItem.objects.values_list('category', flat=True).distinct()
        print(f"Categories: {list(categories)}")  # Debug print
        
        # Get cart items for the current user
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        cart_count = cart_items.count()
        
        # If no items exist, populate the menu
        if not menu.exists():
            print("No menu items found, populating menu...")  # Debug print
            call_command('populate_menu')
            menu = MenuItem.objects.all().order_by('category', 'name')
            categories = MenuItem.objects.values_list('category', flat=True).distinct()
            print(f"After population - Number of menu items: {menu.count()}")  # Debug print
        
        context = {
            'menu': menu,
            'categories': categories,
            'cart_count': cart_count,
            'debug_info': {
                'menu_count': menu.count(),
                'categories': list(categories)
            }
        }
        
        print("Rendering order template with context:", context)  # Debug print
        return render(request, 'menu/order.html', context)
    except Exception as e:
        print(f"Error in order view: {str(e)}")  # Debug print
        return render(request, 'menu/order.html', {
            'error': 'Failed to load menu items. Please try again later.'
        })

@login_required
def checkout(request):
    try:
        if request.method == 'POST':
            # Handle Razorpay order creation
            data = json.loads(request.body)
            amount = data.get('amount')
            currency = data.get('currency', 'INR')
            
            print(f"Creating Razorpay order with amount: {amount}, currency: {currency}")  # Debug log
            
            # Initialize Razorpay client
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            except Exception as e:
                print(f"Razorpay client initialization error: {str(e)}")  # Debug log
                return JsonResponse({
                    'success': False,
                    'error': 'Payment gateway initialization failed. Please try again later.'
                }, status=500)
            
            # Create Razorpay order
            order_data = {
                'amount': amount,
                'currency': currency,
                'payment_capture': 1,
                'notes': {
                    'user_id': request.user.id,
                    'order_type': 'takeaway'
                }
            }
            
            print(f"Order data: {order_data}")  # Debug log
            
            try:
                # Create order
                order = client.order.create(data=order_data)
                print(f"Order created successfully: {order}")  # Debug log
                
                # Create payment link with valid phone number format
                payment_link_data = {
                    'amount': amount,
                    'currency': currency,
                    'accept_partial': False,
                    'description': 'Food Order Payment',
                    'customer': {
                        'name': request.user.get_full_name() or 'Customer',
                        'contact': '9876543210',  # Valid 10-digit phone number
                        'email': request.user.email
                    },
                    'notify': {
                        'sms': True,
                        'email': True
                    },
                    'reminder_enable': True,
                    'notes': {
                        'order_id': order['id'],
                        'user_id': request.user.id
                    },
                    'callback_url': request.build_absolute_uri(reverse('menu:payment_success')),
                    'callback_method': 'get'
                }
                
                print(f"Creating payment link with data: {payment_link_data}")  # Debug log
                
                try:
                    payment_link = client.payment_link.create(payment_link_data)
                    print(f"Payment link created successfully: {payment_link}")  # Debug log
                    
                    return JsonResponse({
                        'success': True,
                        'order_id': order['id'],
                        'amount': amount,
                        'currency': currency,
                        'payment_link': payment_link['short_url']
                    })
                except Exception as e:
                    print(f"Payment link creation error: {str(e)}")  # Debug log
                    return JsonResponse({
                        'success': False,
                        'error': f'Failed to create payment link: {str(e)}'
                    }, status=500)
                    
            except razorpay.errors.BadRequestError as e:
                print(f"Razorpay BadRequestError: {str(e)}")  # Debug log
                return JsonResponse({
                    'success': False,
                    'error': f'Payment gateway error: {str(e)}'
                }, status=400)
            except Exception as e:
                print(f"Razorpay error: {str(e)}")  # Debug log
                return JsonResponse({
                    'success': False,
                    'error': f'Payment gateway error: {str(e)}'
                }, status=500)
            
        # For GET request, show checkout page
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        subtotal = sum(item.item.price * item.quantity for item in cart_items)
        cgst = subtotal * 0.09
        sgst = subtotal * 0.09
        total = subtotal + cgst + sgst
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'cgst': cgst,
            'sgst': sgst,
            'total': total,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID
        }
        
        return render(request, 'menu/checkout.html', context)
        
    except Exception as e:
        print(f"Error in checkout view: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)

@csrf_exempt
def payment_success(request):
    try:
        # Get payment data from request
        payment_data = json.loads(request.body)
        
        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_payment_id': payment_data['razorpay_payment_id'],
            'razorpay_order_id': payment_data['razorpay_order_id'],
            'razorpay_signature': payment_data['razorpay_signature']
        }
        
        client.utility.verify_payment_signature(params_dict)
        
        # Payment is successful, proceed with order placement
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Payment verification failed: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def payment_failure(request):
    try:
        # Get payment data from request
        payment_data = json.loads(request.body)
        print(f"Payment failed: {payment_data}")
        
        return JsonResponse({'success': False, 'error': 'Payment failed'})
        
    except Exception as e:
        print(f"Payment failure handling error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get cart items
            cart_items = Cart.objects.filter(user=request.user).select_related('item')
            if not cart_items.exists():
                return JsonResponse({'error': 'Your cart is empty'}, status=400)
            
            # Calculate totals
            subtotal = sum(item.item.price * item.quantity for item in cart_items)
            tax = subtotal * 0.05
            total = subtotal + tax
            
            # Here you would typically:
            # 1. Create an Order record
            # 2. Create OrderItem records
            # 3. Send confirmation email
            # 4. Clear the cart
            
            # For now, we'll just clear the cart
            cart_items.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Order placed successfully!',
                'order_details': {
                    'name': data.get('name'),
                    'phone': data.get('phone'),
                    'address': data.get('address'),
                    'landmark': data.get('landmark'),
                    'instructions': data.get('instructions'),
                    'subtotal': subtotal,
                    'tax': tax,
                    'total': total
                }
            })
        except Exception as e:
            print(f"Error in place_order: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def order_confirmation(request):
    return render(request, 'menu/order_confirmation.html')

@login_required
def view_cart(request):
    try:
        # Get cart items for the current user
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        
        # Calculate total
        total = sum(item.item.price * item.quantity for item in cart_items)
        
        # Prepare cart data
        cart_data = []
        for cart_item in cart_items:
            item_data = {
                'id': cart_item.id,
                'item': {
                    'id': cart_item.item.id,
                    'name': cart_item.item.name,
                    'price': float(cart_item.item.price),
                    'image': cart_item.item.image.url if cart_item.item.image else None
                },
                'quantity': cart_item.quantity
            }
            cart_data.append(item_data)
        
        return JsonResponse({
            'cart_items': cart_data,
            'total': float(total)
        })
    except Exception as e:
        print(f"Error in view_cart: {str(e)}")  # Debug print
        return JsonResponse({
            'cart_items': [],
            'total': 0,
            'error': 'Failed to load cart items. Please try again later.'
        }, status=500)

@login_required
def x_page(request):
    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'menu/x.html', context)

def logout_view(request):
    logout(request)
    return redirect('menu:login')

@csrf_exempt
def webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
    try:
        payload = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        # Verify webhook signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
        
        data = json.loads(payload)
        event = data.get('event')

        # Handle different webhook events
        if event == 'payment.captured':
            payment_data = data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')
            
            # Get the order details
            order = client.order.fetch(order_id)
            user_id = order.get('notes', {}).get('user_id')
            
            if user_id:
                # Clear the user's cart
                Cart.objects.filter(user_id=user_id).delete()
                
                # You can also create an Order record here
                # Order.objects.create(
                #     user_id=user_id,
                #     order_id=order_id,
                #     payment_id=payment_id,
                #     amount=payment_data.get('amount') / 100,  # Convert from paise to rupees
                #     status='completed'
                # )
                
                print(f"Payment captured for user {user_id}: {payment_data}")
                return JsonResponse({'status': 'success'})
            
        elif event == 'payment.failed':
            payment_data = data.get('payload', {}).get('payment', {}).get('entity', {})
            print(f"Payment failed: {payment_data}")
            
        return JsonResponse({'status': 'success'})
        
    except razorpay.errors.SignatureVerificationError:
        print("Webhook signature verification failed")
        return JsonResponse({'status': 'failure'}, status=400)
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)

def login_view(request):
    return render(request, 'menu/login.html')

def admin_view(request):
    if not request.user.is_staff:
        return redirect('menu:login')
    return render(request, 'menu/admin.html')