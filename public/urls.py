from django.urls import path
from public import views

app_name = 'public'
urlpatterns = [
    path('public/authors/<int:pk>/about/',
         views.AboutPageView.as_view(), name='about-page')
]
