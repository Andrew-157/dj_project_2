from django.db import models
from django.db.models import Avg
from django.db.models.query_utils import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from users.models import CustomUser
from core.models import SocialMedia, UserDescription, Article, FavoriteArticles, Reaction


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


class ArticleDetailView(View):
    nonexistent_template = 'core/nonexistent.html'
    template_name = 'public/article_detail.html'

    def get_favorite(self, user):
        return FavoriteArticles.objects.\
            filter(user=user).prefetch_related('articles').first()

    def get_article(self, pk):
        return Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(pk=pk).first()

    def set_favorite_status(self, user, article):
        if not user.is_authenticated:
            return 'Add to Favorites'
        favorite = self.get_favorite(user)
        if (not favorite) or (article not in favorite.articles.all()):
            return 'Add to Favorites'
        else:
            return 'Remove from Favorites'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        favorite_status = self.set_favorite_status(current_user, article)
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': False})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if current_user.is_authenticated:
            article.times_read += 1
            article.save()
        favorite_status = self.set_favorite_status(current_user, article)
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': True})


class LeaveReactionBaseClass(View):
    is_dislike = False
    is_like = False
    info_message = ''
    redirect_to = 'public:article-detail'
    nonexistent_template = 'core/nonexistent.html'

    def get_article(self, pk):
        return Article.objects.filter(pk=pk).first()

    def get_reaction(self, user, article):
        return Reaction.objects.\
            select_related('user').\
            select_related('article').\
            filter(
                Q(article=article) &
                Q(user=user)
            ).first()

    def leave_dislike(self, user, article: Article, reaction: Reaction):
        if reaction:
            if reaction.value == 1:
                reaction.value = -1
                reaction.save()
            elif reaction.value == -1:
                reaction.delete()
        else:
            reaction = Reaction(user=user,
                                article=article,
                                value=-1)
            reaction.save()

    def leave_like(self, user, article: Article, reaction: Reaction):
        if reaction:
            if reaction.value == -1:
                reaction.value = 1
                reaction.save()
            elif reaction.value == 1:
                reaction.delete()
        else:
            reaction = Reaction(user=user,
                                article=article,
                                value=1)
            reaction.save()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        reaction = self.get_reaction(current_user, article)
        if self.is_dislike:
            self.leave_dislike(current_user, article, reaction)
        if self.is_like:
            self.leave_like(current_user, article, reaction)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))


class LeaveLikeView(LeaveReactionBaseClass):
    is_like = True
    info_message = 'You cannot leave like while you are not authenticated'


class LeaveDislikeView(LeaveReactionBaseClass):
    is_dislike = True
    info_message = 'You cannot leave dislike while you are not authenticated'
