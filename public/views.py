from typing import Any, Dict
from django.db import models
from django.db.models import Avg
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from taggit.models import Tag
from users.models import CustomUser
from core.models import Subscription, SocialMedia, UserDescription, Article, FavoriteArticles, Reaction, Comment, UserReading
from public.forms import CommentArticleForm


class AboutPageView(View):
    template_name = 'public/about_page.html'
    nonexistent_template = 'core/nonexistent.html'

    def get_author(self, pk):
        return CustomUser.objects.filter(pk=pk).first()

    def get_description(self, user):
        return UserDescription.objects.\
            filter(user=user).first()

    def get_social_media(self, user):
        return SocialMedia.objects.\
            filter(user=user).all().\
            order_by('title')

    def get_readings(self, author):
        return Article.objects.filter(
            author=author).all().aggregate(Sum('times_read'))

    def get(self, request, *args, **kwargs):
        author = self.get_author(self.kwargs['pk'])
        if not author:
            return render(self.nonexistent_template)
        description = self.get_description(author)
        social_media_list = self.get_social_media(author)
        readings = self.get_readings(author)['times_read__sum']
        return render(request, self.template_name, {'description': description,
                                                    'social_media_list': social_media_list,
                                                    'author': author,
                                                    'readings': readings})


class ArticleDetailView(View):
    nonexistent_template = 'core/nonexistent.html'
    template_name = 'public/article_detail.html'

    def get_article(self, pk):
        return Article.objects.\
            select_related('author').\
            filter(pk=pk).first()

    def get_favorite(self, user):
        return FavoriteArticles.objects.\
            filter(user=user).first()

    def get_subscription(self, user, author):
        return Subscription.objects.filter(
            Q(subscriber=user) &
            Q(subscribe_to=author)
        ).first()

    def manage_user_readings(self, article, user):
        user_readings = UserReading.objects.\
            filter(
                Q(article=article) &
                Q(user=user)
            ).all()
        exists_for_current_date = False
        user_reading_index = None

        for index, user_reading in enumerate(user_readings):
            if user_reading.date_read.date() == timezone.now().date():
                exists_for_current_date = True
                user_reading_index = index
        if exists_for_current_date:
            user_reading: UserReading = user_readings[user_reading_index]
            user_reading.date_read = timezone.now()
            user_reading.save()
            return None
        else:
            user_reading = UserReading(
                user=user,
                article=article,
                date_read=timezone.now()
            )
            user_reading.save()
            return None

    def get_reaction(self, user, article):
        return Reaction.objects.\
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

    def set_subscription_status(self, user, author):
        if not user.is_authenticated:
            return 'Subscribe'
        subscription = self.get_subscription(user, author)
        if not subscription:
            return 'Subscribe'
        else:
            return 'Unsubscribe'

    def get_likes(self, article):
        likes = Reaction.objects.filter(
            Q(article=article) &
            Q(value=1)
        ).all()
        if not likes:
            return []
        else:
            return likes

    def get_dislikes(self, article):
        dislikes = Reaction.objects.filter(
            Q(article=article) &
            Q(value=-1)
        ).all()
        if not dislikes:
            return []
        return dislikes

    def get_subscribers(self, author):
        return Subscription.objects.\
            filter(subscribe_to=author).count()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        favorite_status = self.set_favorite_status(current_user, article)
        reaction_status = self.set_reaction_status(current_user, article)
        subscription_status = self.set_subscription_status(
            current_user, article.author)
        likes = len(self.get_likes(article))
        dislikes = len(self.get_dislikes(article))
        subscribers = self.get_subscribers(article.author)
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': False,
                                                    'reaction_status': reaction_status,
                                                    'subscription_status': subscription_status,
                                                    'likes': likes,
                                                    'dislikes': dislikes,
                                                    'subscribers': subscribers})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        if current_user.is_authenticated:
            article.times_read += 1
            article.save()
        favorite_status = self.set_favorite_status(current_user, article)
        reaction_status = self.set_reaction_status(current_user, article)
        likes = len(self.get_likes(article))
        dislikes = len(self.get_dislikes(article))
        subscribers = self.get_subscribers(article.author)
        subscription_status = self.set_subscription_status(
            current_user, article.author)
        if current_user.is_authenticated:
            self.manage_user_readings(article, current_user)
        return render(request, self.template_name, {'article': article,
                                                    'favorite_status': favorite_status,
                                                    'show_content': True,
                                                    'reaction_status': reaction_status,
                                                    'subscription_status': subscription_status,
                                                    'likes': likes,
                                                    'dislikes': dislikes,
                                                    'subscribers': subscribers})


class CommentsByArticleList(ListView):
    model = Comment
    template_name = 'public/comments_by_article.html'
    context_object_name = 'comments'

    def get_queryset(self):
        article_id = self.kwargs['pk']
        article = Article.objects.filter(id=article_id).first()
        if not article:
            self.template_name = 'core/nonexistent.html'
            return None
        comments = Comment.objects.\
            select_related('user').filter(article=article).\
            order_by('pub_date').all()
        return comments

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        article = Article.objects.filter(id=self.kwargs['pk']).first()
        context['article'] = article
        return context


class AddRemoveFavoriteArticle(View):
    nonexistent_template = 'core/nonexistent.html'
    redirect_to = 'public:article-detail'
    success_remove = 'You successfully removed this article from your favorites'
    success_add = 'You successfully added this article to your favorites'
    info_message = 'Please, become an authenticated user to add this article to your favorites'
    not_allowed_template = 'core/not_allowed.html'

    def get_favorite(self, user):
        return FavoriteArticles.objects.\
            filter(user=user).first()

    def get_article(self, pk):
        return Article.objects.filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        return render(request, self.not_allowed_template)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        favorite = self.get_favorite(current_user)
        if not favorite:
            # If user have never added any articles to favorites
            # then when they hit this view we both create new instance of
            # FavoriteArticles and add new article in many-to-many relationship
            # between FavoriteArticles and Article models
            favorite = FavoriteArticles(user=current_user)
            favorite.save()
            favorite.articles.add(article)
            messages.success(request, self.success_add)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        # If user already has FavoriteArticles instance
        # we check if article in many-to-many relationship
        if article not in favorite.articles.all():
            # If not we add and return appropriate message about it
            favorite.articles.add(article)
            messages.success(request, self.success_add)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
        else:
            # If it article is there, we remove it and return appropriate message about it
            favorite.articles.remove(article)
            messages.success(request, self.success_remove)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))


class LeaveReactionBaseClass(View):
    is_dislike = False
    is_like = False
    info_message = ''
    redirect_to = 'public:article-detail'
    nonexistent_template = 'core/nonexistent.html'
    not_allowed_template = 'core/not_allowed.html'

    def get_article(self, pk):
        return Article.objects.filter(pk=pk).first()

    def get_reaction(self, user, article):
        return Reaction.objects.\
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
        return render(request, self.not_allowed_template)

    def post(self, request, *args, **kwargs):
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
    redirect_to = 'public:article-comments'
    form_class = CommentArticleForm
    info_message = 'To leave a comment on this article,please become an authenticated user.'
    success_message = 'You successfully published a comment on this article.'
    template_name = 'public/comment_article.html'

    def get_article(self, pk):
        return Article.objects.filter(pk=pk).first()

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
        if not article:
            return render(self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id, )))
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
    redirect_to = 'public:article-comments'
    success_message = 'You successfully deleted your comment on this article'
    not_allowed_template = 'core/not_allowed.html'

    def get_comment(self, pk):
        return Comment.objects.\
            filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        return render(request, self.not_allowed_template)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        comment = self.get_comment(self.kwargs['pk'])
        if not comment:
            return render(request, self.nonexistent_template)
        if comment.user != current_user:
            return render(request, self.not_yours_template)
        article_id = comment.article.id
        comment.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(article_id, )))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UpdateCommentView(View):
    nonexistent_template = 'core/nonexistent.html'
    redirect_to = 'public:article-comments'
    not_yours_template = 'core/not_yours.html'
    form_class = CommentArticleForm
    success_message = 'You successfully updated your comment on this article.'
    template_name = 'public/update_comment.html'

    def get_comment(self, pk):
        return Comment.objects.\
            select_related('article').\
            filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        comment = self.get_comment(self.kwargs['pk'])
        if not comment:
            return render(request, self.nonexistent_template)
        if comment.user != current_user:
            return render(request, self.not_yours_template)
        form = self.form_class(instance=comment)
        return render(request, self.template_name, {'comment': comment,
                                                    'form': form,
                                                    'article': comment.article})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        comment = self.get_comment(self.kwargs['pk'])
        if not comment:
            return render(request, self.nonexistent_template)
        if comment.user != current_user:
            return render(request, self.not_yours_template)
        form = self.form_class(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(comment.article.id, )))
        return render(request, self.template_name, {'comment': comment,
                                                    'form': form,
                                                    'article': comment.article})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SubscribeUnsubscribeThroughArticleDetail(View):
    """
    This view is called in 'article_detail.html' template,
    and it redirects back to 'public:article-detail' view
    """
    nonexistent_template = 'core/nonexistent.html'
    info_message_to_anonymous_user = 'You cannot subscribe while you are not authenticated'
    info_message_to_auth_user = 'You cannot subscribe to yourself'
    redirect_to = 'public:article-detail'
    success_message_subscribed = 'You successfully subscribed to this author'
    success_message_unsubscribed = 'You successfully unsubscribed from this author'
    not_allowed_template = 'core/not_allowed.html'

    def get_article(self, pk):
        return Article.objects.\
            filter(pk=pk).first()

    def get_subscription(self, user, author):
        return Subscription.objects.filter(
            Q(subscriber=user) &
            Q(subscribe_to=author)
        ).first()

    def get(self, request, *args, **kwargs):
        return render(request, self.not_allowed_template)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message_to_anonymous_user)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id,)))
        author = article.author
        if author == current_user:
            messages.info(request, self.info_message_to_auth_user)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id,)))
        subscription = self.get_subscription(current_user, author)
        if not subscription:
            subscription = Subscription(
                subscriber=current_user,
                subscribe_to=author
            )
            subscription.save()
            success_message = self.success_message_subscribed
        else:
            subscription.delete()
            success_message = self.success_message_unsubscribed
        messages.success(request, success_message)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(article.id,)))


class ArticlesByTag(ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'public/articles_by_tag.html'

    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag_object = Tag.objects.filter(slug=tag_slug).first()
        articles = Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(tags=tag_object).\
            order_by('-times_read').all()
        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = ' '.join(self.kwargs['slug'].split('-'))
        return context


class SearchArticlesView(View):
    nonexistent_template = 'core/nonexistent.html'
    template_name = 'public/search_results.html'

    def get_articles(self, search_string):
        return Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(
                Q(title__icontains=search_string) |
                Q(author__username__icontains=search_string)
            ).order_by('-times_read').all()

    def convert_tag_to_slug(self, tag: str):
        # this method is needed if
        # someone enters something like this: #pop music
        if ' ' in tag:
            return '-'.join(tag.split())
        else:
            return tag

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        if query:
            if len(query) == 1 and query == '#':
                return render(request, 'core/empty_search.html')
            if query[0] == '#':
                tag_slug = self.convert_tag_to_slug(query[1:])
                return HttpResponseRedirect(reverse('public:articles-tag', args=(tag_slug, )))
            articles = self.get_articles(query)
            return render(request, self.template_name, {'articles': articles,
                                                        'query': query})
        return render(request, 'core/empty_search.html')

    # def post(self, request, *args, **kwargs):
    #     search_string = request.POST['search_string']
    #     if not search_string:
    #         return render(request, self.nonexistent_template)
    #     if len(search_string) == 1 and search_string[0] == '#':
    #         return render(request, self.nonexistent_template)
    #     if search_string[0] == '#':
    #         tag = self.convert_tag_to_slug(search_string[1:])
    #         return HttpResponseRedirect(reverse('public:articles-tag', args=(tag,)))
    #     articles = self.get_articles(search_string)

    #     return render(request, self.template_name, {'articles': articles,
    #                                                 'search_string': search_string})


class AuthorPageView(View):
    template_name = 'public/author_page.html'
    nonexistent_template = 'core/nonexistent.html'

    def get_author(self, pk):
        return CustomUser.objects.filter(pk=pk).first()

    def get_subscribers(self, author):
        return Subscription.objects.\
            filter(subscribe_to=author).\
            count()

    def get_subscription(self, user, author):
        return Subscription.objects.filter(
            Q(subscriber=user) &
            Q(subscribe_to=author)
        ).first()

    def set_subscription_status(self, user, author):
        if not user.is_authenticated:
            return 'Subscribe'
        subscription = self.get_subscription(user, author)
        if not subscription:
            return 'Subscribe'
        else:
            return 'Unsubscribe'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        author = self.get_author(self.kwargs['pk'])
        if not author:
            return render(request, self.nonexistent_template)
        subscription_status = self.set_subscription_status(
            current_user, author)
        subscribers = self.get_subscribers(author)
        return render(request, self.template_name, {'author': author,
                                                    'subscription_status': subscription_status,
                                                    'subscribers': subscribers})


class SubscribeUnsubscribeThroughAuthorPageView(View):
    nonexistent_template = 'core/nonexistent.html'
    info_message_to_anonymous_user = 'You cannot subscribe while you are not authenticated'
    info_message_to_auth_user = 'You cannot subscribe to yourself'
    redirect_to = 'public:author-page'
    success_message_subscribed = 'You successfully subscribed to this author'
    success_message_unsubscribed = 'You successfully unsubscribed from this author'
    not_allowed_template = 'core/not_allowed.html'

    def get_author(self, pk):
        return CustomUser.objects.filter(pk=pk).first()

    def get_subscription(self, user, author):
        return Subscription.objects.filter(
            Q(subscriber=user) &
            Q(subscribe_to=author)
        ).first()

    def get(self, request, *args, **kwargs):
        return render(request, self.not_allowed_template)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        author = self.get_author(self.kwargs['pk'])
        if not author:
            return render(request, self.nonexistent_template)
        if not current_user.is_authenticated:
            messages.info(request, self.info_message_to_anonymous_user)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(author.id, )))
        if current_user == author:
            messages.info(request, self.info_message_to_auth_user)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(author.id, )))
        subscription = self.get_subscription(current_user, author)
        if not subscription:
            subscription = Subscription(
                subscriber=current_user,
                subscribe_to=author
            )
            subscription.save()
            success_message = self.success_message_subscribed
        else:
            subscription.delete()
            success_message = self.success_message_unsubscribed
        messages.success(request, success_message)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(author.id, )))


class ArticlesByAuthor(View):
    nonexistent_template = 'core/nonexistent.html'
    template_name = 'public/articles_by_author.html'

    def get_author(self, pk):
        return CustomUser.objects.filter(pk=pk).first()

    def get_articles(self, author):
        return Article.objects.\
            prefetch_related('tags').\
            filter(author=author).\
            order_by('-times_read').all()

    def get(self, request, *args, **kwargs):
        author = self.get_author(self.kwargs['pk'])
        if not author:
            return render(request, self.nonexistent_template)
        articles = self.get_articles(author)
        return render(request, self.template_name, {'articles': articles,
                                                    'author': author})
