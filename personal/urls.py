from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'personal'
urlpatterns = [
    path('personal/', views.PersonalPageView.as_view(), name='personal-page'),
    path('personal/social_media/<int:pk>/delete/',
         views.DeleteSocialMediaView.as_view(), name='social_media-delete'),
    path('personal/articles/publish/',
         views.PublishArticleView.as_view(), name='publish-article'),
    path('personal/articles/<int:pk>/update/',
         views.UpdateArticleView.as_view(), name='update-article')
]
