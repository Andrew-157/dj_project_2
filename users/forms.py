from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm,\
    UserChangeForm as BaseUserChangeForm
from users.models import CustomUser


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 'user_image'
        ]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).exists():
            msg = 'A user with that email already exists.'
            self.add_error('email', msg)

        return self.cleaned_data


class UserChangeForm(BaseUserChangeForm):
    email = forms.EmailField(
        required=True, help_text='Required. Enter a valid email address.')
    password = None

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'user_image'
        ]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = self.cleaned_data['username']
        current_user = CustomUser.objects.filter(username=username).first()
        user_with_email = CustomUser.objects.filter(email=email).first()
        if user_with_email and user_with_email != current_user:
            msg = 'A user with that email already exists.'
            self.add_error('email', msg)

        return self.cleaned_data
