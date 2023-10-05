from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class EmailLoginForm(forms.Form):
    email = forms.EmailField()