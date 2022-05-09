from itertools import product
from unicodedata import category
import io
import datetime
from PIL import Image
from io import StringIO

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.core.files import File


from UZone import settings
from .forms import ProductForm, AddressForm
from .models import Category, User, Product, Address, Order, OrderLine
" Creates a test image "


def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
    """
    Generate a test image, returning the filename that it was saved as.

    If ``storage`` is ``None``, the BytesIO containing the image data
    will be passed instead.
    """
    data = io.BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)


# Test cases for views.
" Test login page "


class LogInTest(TestCase):
    def setUp(self):
        self.data1 = {
            'email': 'partner@gmail.com',
            'password': 'secret',
            'role': 'partner'}
        self.data2 = {
            'email': 'cutomer@gmail.com',
            'password': 'secret',
            'role': 'customer'}

        User.objects.create_user(**self.data1)
        User.objects.create_user(**self.data2)

    def test_login_with_partner(self):
        # import pdb; pdb.set_trace()
        response = self.client.post('/user/login/', self.data1, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/user/partnerHome/')

    def test_login_with_customer(self):
        response = self.client.post('/user/login/', self.data2, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/')


" Test ProductView "


class ProductListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        partner = User.objects.create_user(
            email="t@gmail.com", password="password", role="partner")
        category = Category.objects.create(category="men's", user=partner)

        # Create 10 product for pagination test
        product_list = []
        for i in range(7):
            product_list.append(Product(
                user=partner, name="watch", category=category, image="try.jpg", price=23))
        Product.objects.bulk_create(product_list)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/product/')
        self.assertRedirects(response, '/user/login/?next=/product/')

    def test_redirect_to_product_if_logged_in(self):
        login = self.client.login(email="t@gmail.com", password="password")

        response = self.client.get(reverse('store:product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product.html')

    def test_pagination_is_4(self):
        login = self.client.login(email="t@gmail.com", password="password")

        response = self.client.get(reverse('store:product'))
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['object_list']), 4)

    def test_second_page(self):
        # Get second page and confirm it has (exactly) remaining 3 products
        login = self.client.login(email="t@gmail.com", password="password")

        response = self.client.get(reverse('store:product')+'?page=2')
        self.assertEqual(len(response.context['object_list']), 3)


" Test AddProductView "


class AddProductTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        partner = User.objects.create_user(
            email="t@gmail.com", password="password", role="partner")
        category = Category.objects.create(
            category="mens", user=partner)
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        cls.data = {"user": partner,
                    "name": "watch",
                    "category": category.id,
                    "image": avatar_file,
                    "price": 23 }

    def test_redirect_if_not_logged_in(self):
        response = self.client.post('/addProduct/')
        self.assertRedirects(response, '/user/login/?next=/addProduct/')

    def test_allow_to_add_product_if_logged_in(self):

        login = self.client.login(email="t@gmail.com", password="password")
        response = self.client.post('/addProduct/', self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('store:product'))


" Test Updateview "


class UpdateProductTest(TestCase):

    def setUp(self):
        # import pdb;pdb.set_trace()
        partner = User.objects.create_user(
            email="t@gmail.com", password="password", role="partner")
        category = Category.objects.create(category="men's", user=partner)

        self.product = Product.objects.create(
            user=partner, name="watch", category=category, image='avatar.png', price=23)

        self.data = {"user": partner,
                    "name": "Phone",
                    "category": category.id,
                    "price": 23 }

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(
            reverse('store:updateProduct', kwargs={'pk': self.product.pk}))
        self.assertTrue(response.url.startswith('/user/login/'))

    def test_allow_to_update_product_if_logged_in(self):
        login = self.client.login(email="t@gmail.com", password="password")
        response = self.client.post(reverse('store:updateProduct', kwargs={
                                    'pk': self.product.pk}), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:product'))


" Test DeleteProductView "


class DeleteProductTest(TestCase):

    def setUp(self):
        # import pdb;pdb.set_trace()
        partner = User.objects.create_user(
            email="t@gmail.com", password="password", role="partner")
        category = Category.objects.create(category="men's", user=partner)
        self.product1 = Product.objects.create(
            user=partner, name="watch", category=category, image="try.jpg", price=23)
        self.product2 = Product.objects.create(
            user=partner, name="watch", category=category, image="try.jpg", price=23)

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(
            reverse('store:deleteProduct', kwargs={'pk': self.product1.pk}))
        self.assertTrue(response.url.startswith('/user/login/'))

    def test_allow_to_product_if_logged_in(self):
        # import pdb; pdb.set_trace()
        login = self.client.login(email="t@gmail.com", password="password")
        response = self.client.post(
            reverse('store:deleteProduct', kwargs={'pk': self.product1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), 1)
        self.assertRedirects(response, reverse('store:product'))


" Test add To cart "


class AddToCartTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(
            email="t@gmail.com", password="password", role="customer")
        category = Category.objects.create(category="men's", user=user1)

        self.product1 = Product.objects.create(
            user=user1, name="watch", category=category, image="try.jpg", price=23)

        self.data = {"user": user1, "mobile": "1111111111", "address": "Indore",
                     "city": "indore", "state": "MP", "zip_code": "111111"}

    def test_add_to_cart_if_logged_in(self):
        login = self.client.login(email="t@gmail.com", password="password")

        # import pdb; pdb.set_trace()
        response = self.client.post(
            reverse('store:cart_add', kwargs={'pk': self.product1.pk}))

        " payment test "
        response = self.client.post(
            reverse('store:payment'), self.data)
        self.assertEqual(response.status_code, 200)


# Test cases for models.

" Tests for Category Model"


class CategoryModelTest(TestCase):
    @classmethod
    def setUp(self):
        user1 = User.objects.create_user(
            email="t@gmail.com", password="password", role="customer")
        self.c = Category.objects.create(
            category='Laptop', user=user1, image='cat.png')

    def test_category_label(self):
        field_label = Category._meta.get_field('category').verbose_name
        self.assertEqual(field_label, 'category')

    def test_image_label(self):
        field_label = Category._meta.get_field('image').verbose_name
        self.assertEqual(field_label, 'image')

    def test_category_max_length(self):
        max_length = Category._meta.get_field('category').max_length
        self.assertEqual(max_length, 25)

    def test_str_method(self):
        self.assertEqual(str(self.c), self.c.category)

" Product model test "
class ProductModelTest(TestCase):
    @classmethod
    def setUp(self):
        user1 = User.objects.create_user(
            email="t@gmail.com", password="password", role="customer")
        self.c = Category.objects.create(
            category='Laptop', user=user1, image='cat.png')
        self.p = Product.objects.create(
            user=user1, name="watch", category=self.c, image="try.jpg", price=23)

    def test_category_label(self):
        field_label = Product._meta.get_field('category').verbose_name
        self.assertEqual(field_label, 'category')

    def test_name_label(self):
        field_label = Product._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_description_null_eq_true(self):
        nullvalue = Product._meta.get_field('description').null
        self.assertTrue(nullvalue)

    def test_string_representaion(self):
        self.assertEqual(str(self.p), self.p.name)


# Test cases for models.
" Tests for ProductForm"
class ProductFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(
            email="t@gmail.com", password="password", role="customer")
        cls.category = Category.objects.create(
            category='Laptop', user=user1, image='cat.png') 
        fake = create_image(None, 'avatar.png')
        cls.fake_file = SimpleUploadedFile('front.png', fake.getvalue())

    def test_product_form_category_field_label(self):
        form = ProductForm()
        self.assertTrue(form.fields['category'].label == 'Category')

    def test_product_form_with_valid(self):
        data = {"name": "watch","category": self.category,"description": "new","price": 23}
        files = {"image": self.fake_file}

        form = ProductForm(data=data, files=files)
        self.assertTrue(form.is_valid())

    def test_product_form_with_negative_price(self):
        data = {"name": "watch","category": self.category,"description": "new","price": -23}
        files = {"image": self.fake_file}
        form = ProductForm(data=data, files=files)

        self.assertFalse(form.is_valid())

    def test_product_form_with_valid_price(self):
        data = {"name": "watch","category": self.category,"description": "new","price": 453}
        files = {"image": self.fake_file}
        form = ProductForm(data=data, files=files)

        self.assertTrue(form.is_valid())

" Tests for AddressForm"
class AddressFormTest(TestCase):

    def test_product_form_category_field_label(self):
        form = AddressForm()
        self.assertTrue(form.fields['mobile'].label == 'Mobile')

    # Tests for mobile field validation
    def test_address_form_with_mobile_lt_10_digit(self):
        form = AddressForm(data={'mobile':1111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':111111})
        self.assertFalse(form.is_valid())

    def test_address_form_with_mobile_gt_10_digit(self):
        form = AddressForm(data={'mobile':111111111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':111111})
        self.assertFalse(form.is_valid())

    def test_address_form_with_valid_mobile(self):
        form = AddressForm(data={'mobile':1111111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':111111})
        self.assertTrue(form.is_valid())

    # Tests for mobile field validation
    def test_address_form_with_zip_lt_6_digit(self):
        form = AddressForm(data={'mobile':1111111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':1111})
        self.assertFalse(form.is_valid())

    def test_address_form_with_zip_gt_6_digit(self):
        form = AddressForm(data={'mobile':1111111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':11111111})
        self.assertFalse(form.is_valid())

    def test_address_form_with_valid_zip(self):
        form = AddressForm(data={'mobile':1111111111, 'address':"Indore", 'city':"Indore",
                                'state':"MP", 'zip_code':111111})
        self.assertTrue(form.is_valid())