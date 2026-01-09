from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Category, Product
from .cart import Cart

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product_list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('store:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('store:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})

from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        
        order = Order.objects.create(user=request.user, address=address, city=city, postal_code=postal_code)
        
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            
        cart.clear()
        return render(request, 'store/order_created.html', {'order': order})
        
    return render(request, 'store/checkout.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/order_history.html', {'orders': orders})
