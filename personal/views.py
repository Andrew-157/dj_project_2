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


class ClearReactionsBaseClass(View):
    success_message = ''
    reaction_value = None
    redirect_to = ''

    def get_reactions(self, user):
        return Reaction.objects.\
            select_related('user').\
            select_related('article').\
            order_by('-reaction_date').\
            filter(
                Q(user=user) &
                Q(value=self.reaction_value)
            ).all()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        reactions = self.get_reactions(current_user)
        reactions.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ClearLikesView(ClearReactionsBaseClass):
    reaction_value = 1
    success_message = 'You successfully cleared your likes'
    redirect_to = 'personal:liked-articles'


class ClearDislikesView(ClearReactionsBaseClass):
    reaction_value = -1
    success_message = 'You successfully cleared your dislikes'
    redirect_to = 'personal:disliked-articles'


class DeleteSingleReactionBaseClass(View):
    redirect_to = ''
    success_message = ''
    nonexistent_template = 'core/nonexistent.html'
    not_yours_template = 'core/not_yours.html'

    def get_reaction(self, pk):
        return Reaction.objects.\
            select_related('user').\
            filter(pk=pk).first()

    def get(self, request, *args, **kwargs):
        current_user = request.user
        reaction = self.get_reaction(self.kwargs['pk'])
        if not reaction:
            return render(request, self.nonexistent_template)
        if reaction.user != current_user:
            return render(request, self.not_yours_template)
        reaction.delete()
        messages.success(request, self.success_message)
        return redirect(self.redirect_to)


class DeleteLikeView(DeleteSingleReactionBaseClass):
    redirect_to = 'personal:liked-articles'
    success_message = 'You successfully deleted one like reaction'


class DeleteDislikeView(DeleteSingleReactionBaseClass):
    redirect_to = 'personal:disliked-articles'
    success_message = 'You successfully deleted one dislike reaction'
