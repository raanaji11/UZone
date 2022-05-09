from django.urls import path
from . import views

from .views import (Home, CategoryListView, ProductDetail, ProductListView, AddProduct, 
                    UpdateProduct, DeleteProduct, ProductDetail, CouponListView, AddCoupon,
                    DeleteCoupon,  WhishlistView, AddToWishlist, RemoveFromWishlist,
                    PaymentView, OrderView, SortView)


app_name = 'store'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('category/', CategoryListView.as_view(), name='category'),

    path('product/', ProductListView.as_view(), name='product'),
    path('addProduct/', AddProduct.as_view(), name='addProduct'),
    path('updateProduct/<int:pk>/', UpdateProduct.as_view(), name='updateProduct'),
    path('deleteProduct/<int:pk>/', DeleteProduct.as_view(), name='deleteProduct'),
    path('productDetail/<int:pk>/', ProductDetail.as_view(), name='productDetail'),

    path('coupon/', CouponListView.as_view(), name='coupon'),
    path('addCoupon/', AddCoupon.as_view(), name='addCoupon'),
    path('deleteCoupon/<int:pk>/', DeleteCoupon.as_view(), name='deleteCoupon'),
    path('sort/', SortView.as_view(), name='sort'),

    path('wishlist/', WhishlistView.as_view(), name='wishlist'),
    path('addtowishlist/', AddToWishlist.as_view(), name='addtowishlist'),
    path('removefromwishlist/<int:pk>/', RemoveFromWishlist.as_view(), name='removefromwishlist'),



    path('add/<int:pk>/', views.cart_add, name='cart_add'),
    path('item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('item_increment/<int:id>/',
         views.item_increment, name='item_increment'),
    path('item_decrement/<int:id>/',
         views.item_decrement, name='item_decrement'),
    path('cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart-detail/',views.cart_detail,name='cart_detail'),
    
    path('payment/',PaymentView.as_view(),name='payment'),
    path('handlerequest/',views.handlerequest,name='handlerequest'),
    path('order/', OrderView.as_view(), name='order'),

]
