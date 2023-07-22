from django.urls import path
from django.views.generic import TemplateView
from core import views


app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('become_user/',
         TemplateView.as_view(template_name='core/become_user.html'), name='become-user'),
]
