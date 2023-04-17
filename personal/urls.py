from django.urls import path
from . import views


app_name = 'personal'
urlpatterns = [
    path('personal/', views.personal_page, name='personal-page'),
    path('personal/articles/publish/',
         views.PublishArticle.as_view(), name='publish-article'),
    path('personal/articles/<int:article_id>/update/',
         views.update_article, name='update-article'),
    path('personal/articles/<int:article_id>/delete/',
         views.delete_article, name='delete-article'),
    path('personal/social_media/add/',
         views.AddSocialMediaLink.as_view(), name='add-social-media'),
    path('personal/social_media/<int:social_media_id>/delete/',
         views.delete_social_media, name='delete-social-media'),
    path('personal/reading_history/',
         views.reading_history, name='reading-history'),
    path('personal/reading_history/clear/',
         views.clear_reading_history, name='clear-history'),
    path('personal/reading_history/<int:article_id>/delete/',
         views.delete_reading, name='delete-reading'),
    path('personal/articles/liked/', views.liked_articles, name='liked-articles'),
    path('personal/articles/disliked/',
         views.disliked_articles, name='disliked-articles'),
    path('personal/subscriptions/', views.subscriptions, name='subscriptions'),
    path('personal/articles/favorites',
         views.favorite_articles, name='favorites'),
    path('personal/articles/favorites/<int:article_id>/',
         views.favorites_request, name='favorites-manage'),
    path('personal/articles/recommended/',
         views.recommended_articles, name='recommended-articles')
]
