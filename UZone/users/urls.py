from django.urls import path
from .views import SignUpView, LoginView, PartnerHome,userLogout, Profile, UpdateProfile
from django.contrib.auth import views as auth_views
app_name = 'users'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', userLogout, name='logout'),
    path('profile/', Profile.as_view(), name='profile'),
    path('updateprofile/<int:pk>/', UpdateProfile.as_view(), name='updateprofile'),

    path('partnerHome/', PartnerHome.as_view(), name='partnerHome'),

    path('resetpassword/', auth_views.PasswordResetView.as_view(template_name='users/resetPassword.html'),name='resetpassword'),
    path('resetpasswordsent/', auth_views.PasswordResetDoneView.as_view(template_name='users/resetPasswordSent.html'),name='resetpasswordsent'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    # path('resetpasswordsent/', auth_views.PasswordResetDoneView.as_view(template_name='users/resetPasswordSent.html'),name='resetpasswordsent'),

]