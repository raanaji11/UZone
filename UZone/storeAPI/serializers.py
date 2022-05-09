from dataclasses import field
from os import defpath
from unicodedata import category

from rest_framework import serializers
from store.models import  User, Category, Product, Wishlist, Order, Address

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile', 'role', 
                'password']

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category','image']
        read_only_fields = ['user']


class ProductSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()
    class Meta:
        model = Product
        fields = ['id','name','price','description','image','category']

    def validate(self, data):
        if data['price'] < 0:
            raise serializers.ValidationError({"error":"plz enter a valid price"})
        return data


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status', 'date', 'order_id', 'amount')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('mobile','address','city','state','zip_code')





