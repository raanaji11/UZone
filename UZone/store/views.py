from locale import currency
from traceback import print_tb
from django.utils import timezone
import datetime
import pytz
import razorpay

from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django. db. models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.views.generic.detail import DetailView

from UZone import settings

from .models import Category, Order, OrderLine, Product, Coupon, Wishlist, Address
from .forms import ProductForm, CouponForm, AddressForm
from .cart import *
from cart.cart import Cart
from .sendEmail import send_email


IST = pytz.timezone('Asia/Kolkata')

# Create your views here.

" Customer's homepage "
class Home(View):
    def get(self, request):
        cat_id = request.GET.get('category') 
        search= request.GET.get('search')
        categories = Category.objects.all()
        products = Product.objects.all().order_by('id')

        if cat_id:
            products = products.filter(category=cat_id).order_by('name')
        if search:
            products = products.filter(Q(name__icontains=search)|Q(category__category__icontains=search))

        paginator = Paginator(products,3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {'categories': categories, 'page_obj': page_obj}
        return render (request, 'store/home.html', context)


" Shows all product's category to partner "   
class CategoryListView(LoginRequiredMixin, ListView):
    login_url = settings.login_url
    model = Category
    template_name = 'store/category.html'
    context_object_name = 'categories'


" Shows all products of partner "
class ProductListView(LoginRequiredMixin, ListView):
    login_url = settings.login_url
    paginate_by = 4
    model = Product
    template_name = 'store/product.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        catID = self.request.GET.get('category')
        qs = super(ProductListView, self).get_queryset(*args, **kwargs).filter(user=self.request.user)

        if catID:
            qs = qs.filter(category=catID)
        return qs


" Partner add their products "
class AddProduct(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = settings.login_url
    model = Product
    template_name = 'store/addProduct.html'
    form_class = ProductForm
    success_url = reverse_lazy('store:product')
    success_message = "Product has been added SUCCESSFULLY...!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)    

" Partner update their products "
class UpdateProduct(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = settings.login_url
    model = Product
    template_name = 'store/updateProduct.html'
    form_class = ProductForm
    success_message = "Product has been updated SUCCESSFULLY...!"
    success_url = reverse_lazy('store:product')


" partner delete their products "
class DeleteProduct(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = settings.login_url
    model = Product
    success_url = reverse_lazy('store:product')
    template_name = 'store/deleteProduct.html'
    success_message = "Product has been deleted SUCCESSFULLY...!"


" Shows product's detail "
class ProductDetail(DetailView):
    model = Product
    template_name = 'store/productDetail.html'       


" Shows partner's coupon "
class CouponListView(LoginRequiredMixin, ListView):
    login_url = settings.login_url
    model = Coupon
    template_name = 'store/coupon.html'
    context_object_name = 'coupons'

    def get_queryset(self, *args, **kwargs):
        qs = super(CouponListView, self).get_queryset(*args, **kwargs).filter(user=self.request.user)
        return qs


" Partner add their coupons "
class AddCoupon(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = settings.login_url
    model = Coupon
    template_name = 'store/addCoupon.html'
    form_class = CouponForm
    success_url = reverse_lazy('store:coupon')
    success_message = "Coupon has been added SUCCESSFULLY...!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)  


" Partner delete their coupons "
class DeleteCoupon(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = settings.login_url
    model = Coupon
    template_name = 'store/deleteCoupon.html'
    success_url = reverse_lazy('store:coupon')
    success_message = "Coupon has been deleted SUCCESSFULLY...!"


" Shows customer's wishlist "
class WhishlistView(LoginRequiredMixin, ListView):
    login_url = settings.login_url
    model = Wishlist
    template_name = "store/wishlist.html"
    context_object_name = 'wishlist'

    def get_queryset(self, *args, **kwargs):
        qs = super(WhishlistView, self).get_queryset(*args, **kwargs).filter(user=self.request.user)
        return qs


" Product added to wishlist "
class AddToWishlist(LoginRequiredMixin,SuccessMessageMixin, View):
    login_url = settings.login_url

    def get(self,request):
        product_id = request.GET.get('product')
        pro_in_wishlist = Wishlist.objects.filter(Q(user=request.user) & Q(product_id=product_id)).count()

        if (pro_in_wishlist) < 1:
            Wishlist.objects.create(user=request.user, product_id=product_id)
            messages.success(request, "Item added to wishlist")
        return redirect("/")


" Remove products from the wishlist "
class RemoveFromWishlist(LoginRequiredMixin,SuccessMessageMixin, DeleteView):
    login_url = settings.login_url
    model = Wishlist
    template_name = 'store/deletewishlist.html'
    success_url = reverse_lazy('store:wishlist')
    success_message = "Item has been removed SUCCESSFULLY...!"


" Razorpay payment functionality "
client = razorpay.Client(auth=(settings.razorpay_id, settings.razorpay_account_id))

class PaymentView(LoginRequiredMixin,View):
    login_url = settings.login_url

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            form.instance.user = self.request.user
            form.save()
        address = form.instance
        cart = Cart(request)
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

        callback_url = 'http://'+ str(get_current_site(request))+ "/handlerequest/"
        razorpay_order = client.order.create(dict(amount=final_price*100,currency=settings.order_currency,
                                            payment_capture='1'))

        order.order_id = razorpay_order['id']
        order.save()
        cart.clear()
        orderlines = OrderLine.objects.filter(order=order)
        context = {'order':order,'order_id':razorpay_order['id'],
                   'final_price':final_price, 'razorpay_merchant_id':settings.razorpay_id,
                   'callback_url':callback_url, 'orderlines':orderlines, 'address':address}
        return render(request, 'store/pay.html', context)


@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id','')
        order_id = request.POST.get('razorpay_order_id','')
        signature = request.POST.get('razorpay_signature','')

        params_dict = {
            'razorpay_payment_id' : payment_id, 
            'razorpay_order_id' : order_id,
            'razorpay_signature' : signature
            }

        order_db = Order.objects.get(order_id=order_id)
        try:
            check = client.utility.verify_payment_signature(params_dict)
            order_db.status = 'success'
            order_db.save()
            send_email(order_db.user.email)
            return render(request, 'store/success.html')

        except:
            order_db.status = 'failed'
            order_db.save()
            return render(request, 'store/failed.html')

" Shows order's list "
class OrderView(LoginRequiredMixin, View):
    login_url = settings.login_url

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        result={}
        for order in orders:
            orderlines = OrderLine.objects.filter(order=order)
            result[order] = orderlines

        context = {'result': result, 'orders':orders}
        return render(request, 'store/order.html', context)


" Sort or Filter products according to price range "
class SortView(View):
    def get(self, request):
        q = request.GET.get('sort')
        if q == "low":
            page_obj =Product.objects.all().order_by("price")
        else:
            page_obj =Product.objects.all().order_by("-price")
        context = {'page_obj': page_obj}
        return render(request, "store/home.html", context)

