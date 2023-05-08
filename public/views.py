from django.db import models
from django.db.models import Avg
from django.db.models.query_utils import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from users.models import CustomUser
from core.models import SocialMedia, UserDescription, Article, FavoriteArticles, Reaction, Comment, UserReading
from public.forms import CommentArticleForm


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

    def get_article(self, pk):
        return Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(pk=pk).first()

    def get_comments(self, article):
        return Comment.objects.\
            select_related('article').\
            select_related('user').\
            order_by('-pub_date').\
            filter(article=article).all()

    def get_favorite(self, user):
        return FavoriteArticles.objects.\
            filter(user=user).prefetch_related('articles').first()

    def get_user_reading(self, article, user):
        return UserReading.objects.\
            select_related('user').\
            select_related('article').\
            filter(
                Q(article=article) &
                Q(user=user)
            ).first()

    def get_reaction(self, user, article):
        return Reaction.objects.\
            select_related('user').\
            select_related('article').\
            filter(
                Q(article=article) &
                Q(user=user)
            ).first()

    def set_favorite_status(self, user, article):
        if not user.is_authenticated:
            return 'Add to Favorites'
        favorite = self.get_favorite(user)
        if (not favorite) or (article not in favorite.articles.all()):
            return 'Add to Favorites'
        else:
            return 'Remove from Favorites'

    def set_reaction_status(self, user, article):
        if not user.is_authenticated:
            return None
        reaction = self.get_reaction(user, article)
        if not reaction:
            return None
        if reaction.value == 1:
            return 'You liked this article'
        else:
            return 'You disliked this article'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        favorite_status = self.set_favorite_status(current_user, article)
        reaction_status = self.set_reaction_status(current_user, article)
        comments = self.get_comments(article)
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': False,
                                                    'reaction_status': reaction_status,
                                                    'comments': comments})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if current_user.is_authenticated:
            article.times_read += 1
            article.save()
        favorite_status = self.set_favorite_status(current_user, article)
        reaction_status = self.set_reaction_status(current_user, article)
        comments = self.get_comments(article)
        if current_user.is_authenticated:
            user_reading = self.get_user_reading(article, current_user)
            if not user_reading:
                user_reading = UserReading(user=current_user,
                                           article=article,
                                           date_read=timezone.now())
                user_reading.save()
            else:
                user_reading.date_read = timezone.now()
                user_reading.save()
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': True,
                                                    'reaction_status': reaction_status,
                                                    'comments': comments})


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


class CommentArticleView(View):
    nonexistent_template = 'core/nonexistent.html'
    redirect_to = 'public:article-detail'
    form_class = CommentArticleForm
    info_message = 'To leave a comment on this article,please become an authenticated user.'
    success_message = 'You successfully published a comment on this article.'
    template_name = 'public/comment_article.html'

    def get_article(self, pk):
        return Article.objects.select_related('author').filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'article': article})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.article = article
            form.instance.user = current_user
            if current_user == article.author:
                form.instance.is_article_author = True
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        return render(request, self.template_name, {'form': form, 'article': article})


class DeleteCommentView(View):
    nonexistent_template = 'core/nonexistent.html'
    not_yours_template = 'core/not_yours.html'
    redirect_to = 'public:article-detail'
    success_message = 'You successfully deleted your comment on this article'

    def get_comment(self, pk):
        return Comment.objects.\
            select_related('article').\
            select_related('user').filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        comment = self.get_comment(self.kwargs['pk'])
        if not comment:
            return render(request, self.nonexistent_template)
        if comment.user != current_user:
            return render(request, self.not_yours_template)
        article_id = comment.article.id
        comment.delete()
        return HttpResponseRedirect(reverse(self.redirect_to, args=(article_id, )))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
