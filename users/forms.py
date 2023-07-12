from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm,\
    UserChangeForm as BaseUserChangeForm
from users.models import CustomUser


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True, help_text='Required. Enter a valid email address.')
    user_image = forms.ImageField(required=False, label='Profile image*',
                                  help_text='You can register without an image.')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 'user_image'
        ]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if username and len(username) < 6:

            msg = 'Username cannot be shorter than 6 characters.'
            self.add_error('username', msg)

        return self.cleaned_data


class UserChangeForm(BaseUserChangeForm):
    email = forms.EmailField(
        required=True, help_text='Required. Enter a valid email address.')
    password = None
    user_image = forms.ImageField(label='Profile image*', required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'user_image'
        ]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if username and len(username) < 6:
            msg = 'Username cannot be shorter than 6 characters.'
            self.add_error('username', msg)

        return self.cleaned_data
