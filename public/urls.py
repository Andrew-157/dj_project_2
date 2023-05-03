from django.urls import path
from public import views

app_name = 'public'
urlpatterns = [
    path('public/authors/<int:pk>/about/',
         views.AboutPageView.as_view(), name='about-page'),
    path('public/articles/<int:pk>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('public/articles/<int:pk>/like/',
         views.LeaveLikeView.as_view(), name='like-article'),
    path('public/articles/<int:pk>/dislike/',
         views.LeaveDislikeView.as_view(), name='dislike-article')
]
