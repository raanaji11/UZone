from posixpath import basename
from django.urls import path, include
from .views import (RegistrationAPI, HomeAPI, CategoryAPI, UpdateDeleteCategoryAPI, ProductAPI,
                    UpdateDeleteProductAPI, WhishlistAPI, AddToWishlistAPI, PaymentViewAPI, AddToCart, 
                    OrderAPI)

app_name = 'storeAPI'


urlpatterns = [
    path('', HomeAPI.as_view(), name='home'),
    path('signup/', RegistrationAPI.as_view(), name='signup'),
    path('category/', CategoryAPI.as_view(), name='category'),
    path('category/<int:pk>/', UpdateDeleteCategoryAPI.as_view(), name='category'),
    path('product/', ProductAPI.as_view(), name='product'),
    path('product/<int:pk>/', UpdateDeleteProductAPI.as_view(), name='product'),
    path('wishlist/', WhishlistAPI.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', AddToWishlistAPI.as_view(), name='wishlist'),
    path('addtocart/<int:pk>/', AddToCart.as_view(), name='cart_add'),
    path('payment/', PaymentViewAPI.as_view(), name='payment'),
    path('order/', OrderAPI.as_view(), name='order')
 ]