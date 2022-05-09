
from logging import exception
from cart.cart import Cart
from django.shortcuts import render, redirect
from .models import Product
from .forms import AddressForm

def cart_add(request, pk):
    cart = Cart(request)
    product = Product.objects.get(id=pk)
    cart.add(product=product)
    return redirect("store:cart_detail")


def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("store:cart_detail")


def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("store:cart_detail")


def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    q = cart.cart.get(str(product.id))
    if q.get('quantity')==1:
        item_clear(request, id)
    else:
        cart.decrement(product=product)
    return redirect("store:cart_detail")


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("store:cart_detail")


def cart_detail(request):
    form = AddressForm()
    return render(request, 'store/cart_detail.html', {'form': form})