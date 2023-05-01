from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'personal'
urlpatterns = [
    path('personal/', TemplateView.as_view(template_name='personal/personal_page.html'),
         name='personal-page'),
    path('articles/publish/', views.PublishArticleView.as_view(),
         name='publish-article'),
]
