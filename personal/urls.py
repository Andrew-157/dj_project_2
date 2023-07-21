from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'personal'
urlpatterns = [
    # View for seeing personal page
    path('personal/', views.PersonalPageView.as_view(), name='personal-page'),
    # Views for publishing, updating, deleting articles
    path('personal/articles/', views.ArticlesListView.as_view(), name='articles-list'),
    path('personal/articles/<int:pk>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('personal/articles/publish/',
         views.PublishArticleView.as_view(), name='publish-article'),
    path('personal/articles/list/<int:pk>/update/',
         views.UpdateArticleThroughArticlesList.as_view(), name='update-article-list'),
    path('personal/articles/<int:pk>/update/',
         views.UpdateArticleThroughArticleDetail.as_view(), name='update-article-detail'),
    path('personal/articles/<int:pk>/delete/',
         views.DeleteArticleView.as_view(), name='delete-article'),
    # Views for manipulations on about page: creating, updating, deleting user's
    # description; creating, deleting social media links, and showing needed information
    # on about page, such as date when user joined the website, how many times
    # user's articles were read, etc..
    path('personal/about/', views.AboutPageView.as_view(), name='about-page'),
    path('personal/about/social_media/<int:pk>/delete/',
         views.DeleteSocialMediaView.as_view(), name='social_media-delete'),
    path('personal/about/description/add/',
         views.PublishUserDescriptionView.as_view(), name='add-user-description'),
    path('personal/about/description/update/', views.UpdateUserDescriptionView.as_view(),
         name='update-user-description'),
    path('personal/about/description/delete/', views.DeleteUserDescriptionView.as_view(),
         name='delete-user-description'),
    # Views for viewing reading history, clearing it completely and
    # deleting particular readings
    path('personal/reading_history/', views.ReadingHistory.as_view(),
         name='reading-history'),
    path('personal/reading_history/clear/', views.ClearReadingHistory.as_view(),
         name='clear-reading-history'),
    path('personal/reading_history/<int:pk>/delete/', views.DeleteUserReading.as_view(),
         name='delete-reading'),
    # views for viewing liked/disliked articles, clearing all likes/dislikes,
    # deleting particular likes/dislikes
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
    # View for seeing users that user is subscribed to
    path('personal/subscriptions/',
         views.SubscriptionsListView.as_view(), name='subscriptions-list'),
    # Views for seeing articles added to Favorites, clearing all favorites,
    # deleting particular articles from Favorites
    path('personal/articles/favorites/',
         views.FavoriteArticlesList.as_view(), name='favorite-articles'),
    path('personal/articles/favorites/<int:pk>/delete/', views.DeleteFavoriteArticle.as_view(),
         name='delete-favorite-article'),
    path('personal/articles/favorites/clear/', views.ClearFavoritesView.as_view(),
         name='clear-favorites')
]
