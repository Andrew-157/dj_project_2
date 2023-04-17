from django.urls import path
from . import views


app_name = 'public'
public = [
    path('public/articles/<int:article_id>/',
         views.public_article, name='public-article'),
    path('public/articles/<int:article_id>/like/',
         views.like_article, name='like-article'),
    path('public/articles/<int:article_id>/dislike/',
         views.dislike_article, name='dislike-article'),
    path('public/articles/<int:article_id>/comment/',
         views.comment_article, name='comment-article'),
    path('public/tags/<str:tag>/',
         views.find_articles_through_tag, name='tag-article'),
    path('public/authors/<str:author>/', views.author_page, name='author-page'),
    path('public/authors/<str:author>/subscribe/',
         views.subscribe_request, name='subscribe'),
    path('public/search/', views.search_articles, name='search-articles'),
    path('public/articles/popular/',
         views.popular_articles, name='popular-articles')
]
