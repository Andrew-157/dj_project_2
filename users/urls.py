from django.urls import path
from users.views import RegisterUserView, LoginUserView, logout_request, ChangeUserView


app_name = 'users'
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_request, name='logout'),
    path('change-acc/', ChangeUserView.as_view(), name='change-user')
]
