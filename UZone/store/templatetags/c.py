from django import template

register = template.Library()

@register.filter(name='in_cart')
def in_cart(product, cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return True
    return False

@register.filter(name='cart_quantity')
def cart_quantity(product, cart):
    for id ,value in cart.items():
        if int(id) == product.id:
            return value.get('quantity')
    return 0    