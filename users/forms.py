from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm,\
    UserChangeForm as BaseUserChangeForm
from users.models import CustomUser


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2'
        ]


class UserChangeForm(BaseUserChangeForm):
    email = forms.EmailField(required=True)
    password = None

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email'
        ]
