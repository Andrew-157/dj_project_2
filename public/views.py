from django.db import models
from django.db.models import Avg
from django.db.models.query_utils import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from users.models import CustomUser
from core.models import SocialMedia, UserDescription, Article, FavoriteArticles


class AboutPageView(View):
    template_name = 'public/about_page.html'
    nonexistent_template = 'core/nonexistent.html'

    def get_author(self, pk):
        return CustomUser.objects.filter(pk=pk).first()

    def get_description(self, user):
        return UserDescription.objects.\
            select_related('user').filter(user=user).first()

    def get_social_media(self, user):
        return SocialMedia.objects.\
            select_related('user').filter(user=user).all()

    def get(self, request, *args, **kwargs):
        author = self.get_author(self.kwargs['pk'])
        if not author:
            return render(self.nonexistent_template)
        description = self.get_description(author)
        social_media_list = self.get_social_media(author)
        return render(request, self.template_name, {'description': description,
                                                    'social_media_list': social_media_list,
                                                    'author': author})


class ArticleDetail(DetailView):
    template_name = 'public/article_detail.html'
    model = Article
    context_object_name = 'article'
    queryset = Article.objects.\
        select_related('author').\
        prefetch_related('tags').all()

    def get_favorite(self, user):
        return FavoriteArticles.objects.prefetch_related('articles').first()

    def get_object(self):
        article_pk = self.kwargs['pk']
        article = Article.objects.filter(pk=article_pk).first()
        if not article:
            self.template_name = 'core/nonexistent.html'
            return None
        self.kwargs['article'] = article
        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        if not current_user.is_authenticated:
            context['favorite_status'] = 'Add to Favorites'
            return context
        favorite = self.get_favorite(current_user)
        article = self.kwargs['article']
        if not favorite or article not in favorite.articles.all():
            context['favorite_status'] = 'Add to Favorites'
        else:
            context['favorite_status'] = 'Remove from favorites'
        return context
