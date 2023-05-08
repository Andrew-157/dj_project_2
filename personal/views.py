from typing import Any, Dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from core.models import Article, SocialMedia, UserDescription, FavoriteArticles, UserReading, Reaction
from personal.forms import PublishUpdateArticleForm, PublishSocialMediaForm, PublishUpdateUserDescriptionForm


class PublishArticleView(View):
    form_class = PublishUpdateArticleForm
    template_name = 'personal/publish_article.html'
    success_message = 'You successfully published new article'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, self.success_message)
            return redirect('personal:personal-page')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UpdateArticleView(View):
    form_class = PublishUpdateArticleForm
    template_name = 'personal/update_article.html'
    success_message = 'You successfully updated your article'
    nonexistent_template = 'core/nonexistent.html'
    not_yours_template = 'core/not_yours.html'

    def get_article(self, pk):
        return Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        article = self.get_article(self.kwargs['pk'])
        if not article:
            return render(request, self.nonexistent_template)
        if article.author != request.user:
            return render(request, self.not_yours_template)
        form = self.form_class(instance=article)
        return render(request, self.template_name, {'form': form, 'article': article})

    def post(self, request, *args, **kwargs):
        article = self.get_article(self.kwargs['pk'])
        form = self.form_class(request.POST, request.FILES, instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            # form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, self.success_message)
            return redirect('personal:personal-page')
        return render(request, self.template_name, {'form': form, 'article': article})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AboutPageView(View):
    template_name = 'personal/about_page.html'
    form_class = PublishSocialMediaForm
    success_message = 'You successfully added new link to your social media'
    redirect_to = 'personal:about-page'

    def get_social_media(self, user):
        return SocialMedia.objects.\
            filter(user=user).\
            order_by('title').\
            all()

    def get_description(self, user):
        return UserDescription.objects.\
            select_related('user').filter(user=user).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        social_media_list = self.get_social_media(current_user)
        description = self.get_description(current_user)
        form = self.form_class()
        return render(request, self.template_name, {'form': form,
                                                    'social_media_list': social_media_list,
                                                    'description': description})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.user = current_user
            form.save()
            messages.success(request, self.success_message)
            return redirect(self.redirect_to)
        social_media_list = self.get_social_media(current_user)
        description = self.get_description(current_user)
        return render(request, self.template_name, {'form': form,
                                                    'social_media_list': social_media_list,
                                                    'description': description})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteSocialMediaView(View):
    success_message = 'You successfully deleted this social media link'
    nonexistent_template = 'core/nonexistent.html'
    not_yours_template = 'core/not_yours.html'
    redirect_to = 'personal:about-page'

    def get_social_media(self, pk):
        return SocialMedia.objects.\
            select_related('user').filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        social_media = self.get_social_media(self.kwargs['pk'])
        if not social_media:
            return render(request, self.nonexistent_template)
        if social_media.user != current_user:
            return render(request, self.not_yours_template)
        social_media.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PublishUserDescriptionView(View):
    warning_message = 'You already have a description, you can either delete or update it'
    success_message = 'You successfully published your description'
    redirect_to = 'personal:about-page'
    form_class = PublishUpdateUserDescriptionForm
    template_name = 'personal/publish_description.html'

    def get_description(self, user):
        return UserDescription.objects.\
            select_related('user').filter(user=user).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        if self.get_description(current_user):
            messages.warning(request, self.warning_message)
            return redirect(self.redirect_to)
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.user = current_user
            form.save()
            messages.success(request, self.success_message)
            return redirect(self.redirect_to)
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UpdateUserDescriptionView(View):
    form_class = PublishUpdateUserDescriptionForm
    template_name = 'personal/update_description.html'
    success_message = 'You successfully updated your description'
    warning_message = 'You cannot update your description, as you do not have one'
    redirect_to = 'personal:about-page'

    def get_description(self, user):
        return UserDescription.objects.\
            select_related('user').filter(user=user).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        description = self.get_description(current_user)
        if not description:
            messages.warning(request, self.warning_message)
            return redirect(self.redirect_to)
        form = self.form_class(instance=description)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        current_user = request.user
        description = self.get_description(current_user)
        form = self.form_class(request.POST, instance=description)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return redirect(self.redirect_to)
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteUserDescriptionView(View):
    success_message = 'You successfully deleted your description'
    warning_message = 'You do not have a description, you cannot delete it'
    redirect_to = 'personal:about-page'

    def get_description(self, user):
        return UserDescription.objects.\
            select_related('user').filter(user=user).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        description = self.get_description(current_user)
        if not description:
            messages.warning(request, self.warning_message)
            return redirect(self.redirect_to)
        description.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AddRemoveFavoriteArticle(View):
    nonexistent_template = 'core/nonexistent.html'
    redirect_to = 'public:article-detail'
    success_remove = 'You successfully removed this article from your favorites'
    success_add = 'You successfully added this article to your favorites'
    info_message = 'Please, become an authenticated user to add this article to your favorites'

    def get_favorite(self, user):
        return FavoriteArticles.objects.\
            prefetch_related('articles').filter(user=user).first()

    def get_article(self, pk):
        return Article.objects.filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
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
            favorite = FavoriteArticles(user=current_user).save()
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


class ReadingHistory(View):
    template_name = 'personal/reading_history.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        user_readings = UserReading.objects.\
            select_related('user').\
            select_related('article').\
            filter(user=current_user).\
            order_by('-date_read').all()
        return render(request, self.template_name, {'user_readings': user_readings})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ClearReadingHistory(View):
    success_message = 'You successfully cleared your reading history'
    redirect_to = 'personal:reading-history'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        user_readings = UserReading.objects.\
            select_related('user').filter(user=current_user).all()
        user_readings.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteUserReading(View):
    success_message = 'You successfully deleted info about reading this article\
        from your reading history'
    not_yours_template = 'core/not_yours.html'
    redirect_to = 'personal:reading-history'
    nonexistent_template = 'core/nonexistent.html'

    def get_user_reading(self, pk):
        return UserReading.objects.select_related('user').\
            filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        user_reading = self.get_user_reading(self.kwargs['pk'])
        if not user_reading:
            return render(request, self.nonexistent_template)
        if user_reading.user != current_user:
            return render(request, self.not_yours_template)
        user_reading.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ReactedArticlesBaseClass(ListView):
    """
    This class will be used as parent class for
    LikedArticlesView and DislikedArticlesView,
    both views will be using the same template,
    but with different message_to_user shown
    and depending on boolean variables liked and disliked,
    buttons to delete liked or disliked article
    """
    reaction_value = None
    model = Reaction
    context_object_name = 'reaction_objects'
    template_name = ''

    def get_queryset(self):
        current_user = self.request.user
        return Reaction.objects.\
            select_related('user').\
            select_related('article').\
            order_by('-reaction_date').\
            filter(
                Q(user=current_user) &
                Q(value=self.reaction_value)
            ).all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class LikedArticlesView(ReactedArticlesBaseClass):
    reaction_value = 1
    template_name = 'personal/liked_articles.html'


class DislikedArticlesView(ReactedArticlesBaseClass):
    reaction_value = -1
    template_name = 'personal/disliked_articles.html'
