from email import message
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from store.models import User
from .forms import LoginForm, SignupForm, ProfileForm
from UZone import settings
# Create your views here.


class SignUpView(SuccessMessageMixin,CreateView):
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')
    form_class = SignupForm
    success_message = "Your registration has been done SUCCESSFULLY. Plz Login....!"

class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email,password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in...!")
            if user.role == "partner":
                return redirect('users:partnerHome')

            if user.role == "customer":
                return redirect("store:home")

        else:
            messages.success(request, "Invalid credentials. Plz try again...")
            return redirect('users:login')

class PartnerHome(View):
    def get(self, request):
        return render(request, 'users/partnerHome.html' )

def userLogout(request):
    logout(request)
    messages.success(request, "Logged out Successfully...!")
    return redirect("store:home")


class Profile(View):
    def get(self, request):
        return render(request, 'users/profile.html')


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = settings.login_url
    model = User
    template_name = 'users/updateProfile.html'
    form_class = ProfileForm
    success_message = "Profile has been updated SUCCESSFULLY...!"
    success_url = reverse_lazy('users:profile')



