from django.urls import path
from . import views


app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('change_user/', views.ChangeUser.as_view(),
         name='change-user'),
    path('password_reset/', views.password_reset_request,
         name='password-reset'),
]
