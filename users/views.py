from django.conf import settings
from django.contrib import messages
from django.db.models.query_utils import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.views import View
from .models import CustomUser
from .forms import CustomUserForm, ChangeCustomUserForm


def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = 'users/password/password_reset_email.txt'
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Articlee",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http"
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email,
                                  'admin@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="users/password/password_reset.html", context={"password_reset_form": password_reset_form})


class RegisterUser(View):
    form_class = CustomUserForm
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to the Articlee')
            return redirect('core:index')

        return render(request, self.template_name, {'form': form})


class LoginUser(View):
    form_class = AuthenticationForm
    template_name = 'users/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(
                    request, f"Welcome back to the Articlee")
                return redirect('core:index')
        return render(request, self.template_name, {'form': form})


def logout_request(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('core:index')


class ChangeUser(View):
    form_class = ChangeCustomUserForm
    template_name = 'users/change_user.html'

    def get(self, request):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        current_user = request.user
        form = self.form_class(
            request.POST, request.FILES, instance=current_user)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f'Your account was successfully changed')
            return redirect('core:index')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
