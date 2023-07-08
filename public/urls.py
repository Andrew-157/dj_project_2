from django.urls import path
from public import views

app_name = 'public'
urlpatterns = [
    path('public/authors/<int:pk>/about/',
         views.AboutPageView.as_view(), name='about-page'),
    path('public/authors/<int:pk>/',
         views.AuthorPageView.as_view(), name='author-page'),
    path('public/articles/<int:pk>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('public/articles/<int:pk>/like/',
         views.LeaveLikeView.as_view(), name='like-article'),
    path('public/articles/<int:pk>/dislike/',
         views.LeaveDislikeView.as_view(), name='dislike-article'),
    path('public/articles/<int:pk>/comment/',
         views.CommentArticleView.as_view(), name='comment-article'),
    path('public/comments/<int:pk>/delete/',
         views.DeleteCommentView.as_view(), name='delete-comment'),
    path('public/articles/<int:pk>/favorites/manage/',
         views.AddRemoveFavoriteArticle.as_view(), name='manage-favorites'),
    path('public/articles/<int:pk>/author/subscribe/',
         views.SubscribeUnsubscribeThroughArticleDetail.as_view(), name='subscription-through-detail'),
    path('public/authors/<int:pk>/subscribe/', views.SubscribeUnsubscribeThroughAuthorPageView.as_view(),
         name='subscription-through-author'),
    path('public/articles/tags/<str:slug>/',
         views.ArticlesByTag.as_view(), name='articles-tag'),
    path('public/articles/search/',
         views.SearchArticlesView.as_view(), name='search'),
    path('public/articles/authors/<int:pk>/', views.ArticlesByAuthor.as_view(),
         name='articles-by-author'),
    path('public/articles/<int:pk>/comments/',
         views.CommentsByArticleList.as_view(), name='article-comments'),
    path('public/articles/comments/<int:pk>/update/', views.UpdateCommentView.as_view(),
         name='update-comment')
]
