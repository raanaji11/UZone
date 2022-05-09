import datetime
from heapq import merge
from itertools import product
from urllib import response
import pytz
from yaml import serialize
from cart.cart import Cart
import razorpay

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django. db. models import Q

from UZone import settings

from store.models import Product, User, Category,Address, Order, OrderLine, Wishlist
from .serializers import (UserSerializer, CategorySerializer, ProductSerializer, WishlistSerializer, 
                            OrderSerializer, AddressSerializer)

IST = pytz.timezone('Asia/Kolkata')
client = razorpay.Client(auth=(settings.razorpay_id, settings.razorpay_account_id))
                 

" Registraton API "
class RegistrationAPI(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
     
        if serializer.is_valid():
            serializer.save()  
            user = User.objects.get(email=serializer.data['email'])
            refresh = RefreshToken.for_user(user)

            return Response({'status':200, 'payload': serializer.data,
                            'refresh':str(refresh), 
                            'access':str(refresh.access_token), 
                            'msg': 'Data saved'})
        return Response({'status':200, 'Error': serializer.errors, 'msg': 'Something went wrong'})
    

" Home API "
class HomeAPI(APIView):
    def get(slelf, request):
        cat_id = request.GET.get('category') 
        search= request.GET.get('search')
        products = Product.objects.all().order_by('id')

        if cat_id:
            products = products.filter(category=cat_id).order_by('name')
        if search:
            products = products.filter(Q(name__icontains=search)|Q(category__category__icontains=search))

        serializer = ProductSerializer(products, many=True)
        return Response({'status':200, 'payload': serializer.data})


" Category API"
class CategoryAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CategorySerializer

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({'status':200, 'payload': serializer.data})

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'status':200, 'payload': serializer.data, 'msg': 'Data saved'})
        return Response({'status':200, 'Error': serializer.errors, 'msg': 'Something went wrong'})
 

class UpdateDeleteCategoryAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def delete(self, request,pk=None):
        category = Category.objects.get(id=pk)
        category.delete()
        return Response({'status':200, 'msg': 'Data deleted'})

    def put(self, request, pk=None):
        category = Category.objects.get(id=pk)
        serializer = CategorySerializer(category, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200, 'payload': serializer.data, 'msg': 'Data saved'})
        return Response({'status':200, 'Error': serializer.errors, 'msg': 'Something went wrong'})
 


" Product API"
class ProductAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = ProductSerializer

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)

        return Response({'status':200, 'payload': serializer.data})
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'status':200, 'payload': serializer.data, 'msg': 'Data saved'})
        return Response({'status':200, 'Error': serializer.errors, 'msg': 'Something went wrong'})
    

class UpdateDeleteProductAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response({'status':200, 'payload': serializer.data})

    def put(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200, 'payload': serializer.data, 'msg': 'Data saved'})
        return Response({'status':200, 'Error': serializer.errors, 'msg': 'Something went wrong'})
    
    def delete(self, request,pk=None):
        product = Product.objects.get(id=pk)
        product.delete()
        return Response({'status':200, 'msg': 'Data deleted'})


" Wishlist API "
class WhishlistAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlists = Wishlist.objects.filter(user=self.request.user)
        serializer = WishlistSerializer(wishlists, many=True)

        return Response({'status':200, 'payload': serializer.data})
 

" API for Add to wishlist "
class AddToWishlistAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request, pk):
        pro_in_wishlist = Wishlist.objects.filter(Q(user=request.user) & Q(product_id=pk)).count()

        if (pro_in_wishlist) < 1:
            wishlist = Wishlist.objects.create(product_id=pk,user=request.user)
            serializer = WishlistSerializer(wishlist)

            return Response({'status':200, 'payload': serializer.data})
        return Response({'status':200,  'msg': 'Item is already in wishlist'})

    def delete(self,request,pk):
        Wishlist.objects.get(Q(user=request.user) & Q(product_id=pk)).delete()
        return Response({'status':200, 'msg': 'Item removed from wishlist'})


" API for add to cart "
class AddToCart(APIView):
    def get(self,request, pk):
        cart = Cart(request)
        product = Product.objects.get(id=pk)
        cart.add(product=product)
        return Response({'status':200, 'msg': 'Item Added to cart'})


" API for payment view "
class PaymentViewAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user) 
        
        cart = Cart(request)
        if cart.cart:
            user = request.user
            today = datetime.datetime.now(IST)
            final_price = 0
            order = Order.objects.create(user=user,date=today,amount=final_price)
            all_orderlines = []
            for product in cart.cart.values():
                quantity = int(product.get('quantity'))
                price = int(product.get('price'))
                product = int(product.get('product_id'))

                all_orderlines.append(OrderLine(user=user, order=order, product_id=product, quantity=quantity))
                final_price += price*quantity
            orderline = OrderLine.objects.bulk_create(all_orderlines)

            order.amount = final_price 

            # callback_url = 'http://'+ str(get_current_site(request))+ "/handlerequest/"
            razorpay_order = client.order.create(dict(amount=final_price*100,currency=settings.order_currency,
                                            payment_capture='1'))

            order.order_id = razorpay_order['id']
            order.save()
            cart.clear()
            order_serializer = OrderSerializer(order)
            return Response({'status':200, 'payload': order_serializer.data}, {"msg":"Order recieved"})
        else:
            return Response("Your cart is Empty..! Plz add some products in cart.")


class OrderAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        order_s = OrderSerializer(orders, many=True)

        return Response({'status':200, 'payload': order_s.data})

