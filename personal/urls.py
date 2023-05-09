from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'personal'
urlpatterns = [
    path('personal/', views.PersonalPageView.as_view(), name='personal-page'),
    path('personal/articles/', views.ArticlesListView.as_view(), name='articles-list'),
    path('personal/articles/<int:pk>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('personal/articles/publish/',
         views.PublishArticleView.as_view(), name='publish-article'),
    path('personal/articles/<int:pk>/update/',
         views.UpdateArticleView.as_view(), name='update-article'),
    path('personal/articles/<int:pk>/delete/',
         views.DeleteArticleView.as_view(), name='delete-article'),
    path('personal/about/', views.AboutPageView.as_view(), name='about-page'),
    path('personal/about/social_media/<int:pk>/delete/',
         views.DeleteSocialMediaView.as_view(), name='social_media-delete'),
    path('personal/about/description/add/',
         views.PublishUserDescriptionView.as_view(), name='add-user-description'),
    path('personal/about/description/update/', views.UpdateUserDescriptionView.as_view(),
         name='update-user-description'),
    path('personal/about/description/delete/', views.DeleteUserDescriptionView.as_view(),
         name='delete-user-description'),
    path('personal/reading_history/', views.ReadingHistory.as_view(),
         name='reading-history'),
    path('personal/reading_history/clear/', views.ClearReadingHistory.as_view(),
         name='clear-reading-history'),
    path('personal/reading_history/<int:pk>/delete/', views.DeleteUserReading.as_view(),
         name='delete-reading'),
    path('personal/articles/liked/',
         views.LikedArticlesView.as_view(), name='liked-articles'),
    path('personal/articles/disliked/',
         views.DislikedArticlesView.as_view(), name='disliked-articles'),
    path('personal/articles/liked/clear/',
         views.ClearLikesView.as_view(), name='clear-likes'),
    path('personal/articles/disliked/clear/',
         views.ClearDislikesView.as_view(), name='clear-dislikes'),
    path('personal/likes/<int:pk>/delete/',
         views.DeleteLikeView.as_view(), name='delete-like'),
    path('personal/dislikes/<int:pk>/delete/',
         views.DeleteDislikeView.as_view(), name='delete-dislike'),
    path('personal/subscriptions/',
         views.SubscriptionsListView.as_view(), name='subscriptions-list')

]
