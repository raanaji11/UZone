from django.contrib import admin
from .models import User, Category, Product, Coupon, Wishlist, Order, OrderLine, Address

# Register your models here.

class UserList(admin.ModelAdmin):
    list_display = ['first_name']

admin.site.register(User, UserList)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Coupon)
admin.site.register(Wishlist)
admin.site.register(OrderLine)
admin.site.register(Order)
admin.site.register(Address)




