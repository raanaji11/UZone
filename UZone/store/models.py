from pyexpat import model
from unicodedata import name
from xml.etree.ElementInclude import default_loader
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

from django.conf import settings
User = settings.AUTH_USER_MODEL

# Create your models here.
class User(AbstractUser):

    role = (
        ('partner', 'partner'),
        ('customer', 'customer'),
    )
    username = None
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20)
    role = models.CharField(max_length=200, choices=role)
    image = models.ImageField(upload_to='uploads/profile',default=None)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Category(models.Model):
    category = models.CharField(max_length=25)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/category',default=None)

    def __str__(self):
        return f"{self.category}"


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    description = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/product')

    def __str__(self):
        return f"{self.name}"


class Coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    code = models.CharField(max_length=8)
    desc = models.CharField(max_length=100)
    discount_percentage = models.IntegerField()
    
    def __str__(self):
        return f"{self.code}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.product}"



class Order(models.Model):

    status = (
        ('pending', 'pending'),
        ('success', 'success'),
        ('failed', 'failed'),
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=status, default='pending')
    date =  models.DateTimeField()
    order_id = models.CharField(max_length=100, default="")
    amount = models.IntegerField()


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.IntegerField()
    address = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=20,default="")
    state = models.CharField(max_length=20, default="")
    zip_code = models.IntegerField()

"""
def sum(a,b):
    if a.isdigit() and b.isdigit():
        other operations, methods calling
        mutiple
        return a+b
    else:
        raise InvalidException("Invalid arguments")
    
    assertEqual(sum(1,2), 3)
    assertEqual(sum(1,'2'), 3)
"""
