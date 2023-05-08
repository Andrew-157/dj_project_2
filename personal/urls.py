from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'personal'
urlpatterns = [
    path('personal/', TemplateView.as_view(template_name='personal/personal_page.html'),
         name='personal-page'),
    path('personal/articles/publish/',
         views.PublishArticleView.as_view(), name='publish-article'),
    path('personal/articles/<int:pk>/update/',
         views.UpdateArticleView.as_view(), name='update-article'),
    path('personal/about/', views.AboutPageView.as_view(), name='about-page'),
    path('personal/about/social_media/<int:pk>/delete/',
         views.DeleteSocialMediaView.as_view(), name='social_media-delete'),
    path('personal/about/description/add/',
         views.PublishUserDescriptionView.as_view(), name='add-user-description'),
    path('personal/about/description/update/', views.UpdateUserDescriptionView.as_view(),
         name='update-user-description'),
    path('personal/about/description/delete/', views.DeleteUserDescriptionView.as_view(),
         name='delete-user-description'),
    path('personal/articles/<int:pk>/favorites/manage/',
         views.AddRemoveFavoriteArticle.as_view(), name='manage-favorites'),
    path('personal/reading_history/', views.ReadingHistory.as_view(),
         name='reading-history')
]
