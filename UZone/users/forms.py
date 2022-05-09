from django import forms 
from django.contrib.auth.forms import UserCreationForm
from store.models import User

class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'mobile', 'role', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data['mobile']

        if len(mobile) < 10 or len(mobile) > 10:
            raise forms.ValidationError("Mobile number be of 10 digits.")

class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email','password')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('image','first_name', 'last_name', 'email', 'mobile')

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data['mobile']

        if len(mobile) < 10 or len(mobile) > 10:
            raise forms.ValidationError("Mobile number be of 10 digits.")
