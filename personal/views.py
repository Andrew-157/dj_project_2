from django.shortcuts import render, redirect
from django.db.models.query_utils import Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from core.models import SocialMedia, Article, Reaction, UserReadings, Comment, Subscription, Favorite
from .forms import SocialMediaForm, PublishArticleForm


class AddSocialMediaLink(View):
    form_class = SocialMediaForm
    template_name = 'personal/add_social_media.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(
                request, 'You successfully added new link to your social media')
            return redirect('personal:personal-page')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required()
def delete_social_media(request, social_media_id):
    current_user = request.user
    social_media = SocialMedia.objects.\
        select_related('user').\
        filter(pk=social_media_id).first()
    if not social_media:
        return render(request, 'core/nonexistent.html')
    if social_media.user != current_user:
        return render(request, 'core/not_yours.html')
    social_media.delete()
    return redirect('personal:personal-page')


class PublishArticle(View):
    form_class = PublishArticleForm
    template_name = 'personal/publish_article.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'You successfully published new article')
            return redirect('core:index')
        return render(request, 'personal/publish_article.html', {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required()
def update_article(request, article_id):
    current_user = request.user
    article = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    if article.author != current_user:
        return render(request, 'core/not_yours.html')
    if request.method == 'POST':
        form = PublishArticleForm(request.POST,
                                  request.FILES,
                                  instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(
                request, 'You successfully updated your article')
            return redirect('personal:personal-page')
    form = PublishArticleForm(instance=article)
    return render(request, 'personal/update_article.html', {'form': form, 'article': article})


@login_required()
def delete_article(request, article_id):
    current_user = request.user
    article = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    if article.author != current_user:
        return render(request, 'core/not_yours.html')
    article.delete()
    messages.success(request, 'Your article was successfully deleted')
    return redirect('personal:personal-page')


@login_required()
def personal_page(request):
    current_user = request.user
    total_readings = None
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        order_by('-pub_date').\
        filter(author=current_user).\
        all()
    if articles:
        total_readings = sum(articles.values_list('times_read', flat=True))
    number_of_articles = len(articles)
    subscribers = Subscription.objects.filter(
        subscribe_to=current_user).count()
    subscriptions = Subscription.objects.\
        filter(subscriber=current_user).count()
    social_media = SocialMedia.objects.\
        filter(user=current_user).all()

    return render(request, 'personal/personal_page.html', {'current_user': current_user,
                                                           'articles': articles,
                                                           'total_readings': total_readings,
                                                           'number_of_articles': number_of_articles,
                                                           'subscribers': subscribers,
                                                           'subscriptions': subscriptions,
                                                           'social_media': social_media})


@login_required()
def reading_history(request):
    current_user = request.user
    user_readings = UserReadings.objects.select_related(
        'article').filter(user=current_user).order_by('-date_read').all()
    number_of_readings = len(user_readings)
    if number_of_readings == 0:
        message_to_display = 'Your reading history is empty'
    else:
        message_to_display = 'This is your reading history'

    return render(request, 'personal/reading_history.html', {'message_to_display': message_to_display,
                                                             'user_readings': user_readings})


@login_required()
def clear_reading_history(request):
    current_user = request.user
    user_readings = UserReadings.objects.\
        select_related('article').filter(user=current_user).all()
    if len(user_readings) == 0:
        messages.info(request, 'Your reading history is already empty')
        return redirect('personal:reading-history')
    reactions_by_user = Reaction.objects.filter(
        reaction_owner=current_user).delete()
    comments_by_user = Comment.objects.filter(
        commentator=current_user
    ).all().delete()
    for user_reading in user_readings:
        article = user_reading.article
        article.times_read -= user_reading.times_read
        article.save()
    user_readings.delete()
    messages.success(request, 'You successfully cleared your reading history')
    return redirect('personal:reading-history')


@login_required()
def delete_reading(request, article_id):
    current_user = request.user
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    user_reading = UserReadings.objects.\
        select_related('article').filter(Q(user=current_user)
                                         & Q(article=article)).first()
    if not user_reading:
        return render(request, 'core/nonexistent.html')
    article.times_read -= user_reading.times_read
    article.save()
    user_reaction = Reaction.objects.\
        filter(Q(article=article)
               & Q(reaction_owner=current_user)).first()
    if user_reaction:
        user_reaction.delete()
    user_comments = Comment.objects.\
        filter(
            Q(article=article)
            & Q(commentator=current_user)
        ).all().delete()
    user_reading.delete()
    messages.success(request, 'Article was deleted from your reading history')
    return redirect('personal:reading-history')


@login_required()
def liked_articles(request):
    current_user = request.user
    reactions = Reaction.objects.select_related('article').filter(Q(reaction_owner=current_user) &
                                                                  Q(value=1)).all()
    number_of_reactions = len(reactions)
    if number_of_reactions == 0:
        message_to_display = 'You have not liked any articles yet'
        articles = None
    else:
        if number_of_reactions == 1:
            message_to_display = 'You totally liked 1 article'
        else:
            message_to_display = f'You totally liked {number_of_reactions} articles'
        articles_ids = [reaction.article.id for reaction in reactions]
        articles = Article.objects.select_related('author').\
            prefetch_related('tags').\
            filter(pk__in=articles_ids).all()
    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})


@login_required()
def disliked_articles(request):
    current_user = request.user
    reactions = Reaction.objects.select_related('article').filter(Q(reaction_owner=current_user) &
                                                                  Q(value=-1)).all()
    number_of_reactions = len(reactions)
    if number_of_reactions == 0:
        message_to_display = 'You have not disliked any articles yet'
        articles = None
    else:
        if number_of_reactions == 1:
            message_to_display = 'You totally disliked 1 article'
        else:
            message_to_display = f'You totally disliked {number_of_reactions} articles'
        articles_ids = [reaction.article.id for reaction in reactions]
        articles = Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(pk__in=articles_ids).all()
    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})


@login_required()
def subscriptions(request):
    current_user = request.user
    subscriptions = Subscription.objects.\
        select_related('subscribe_to').filter(subscriber=current_user).all()
    authors = [subscription.subscribe_to for subscription in subscriptions]
    return render(request, 'personal/subscriptions.html', {'authors': authors})


def favorites_request(request, article_id):
    # View for adding an article to 'Favorites'
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, 'You cannot add an article to "Favorites" while you are not authenticated')
        return HttpResponseRedirect(reverse('public:public-article', args=article_id,))
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    favorite = Favorite.objects.filter(
        Q(owner=current_user) &
        Q(article=article)
    ).first()
    if not favorite:
        favorite = Favorite(
            owner=current_user,
            article=article
        )
        favorite.save()
        messages.success(
            request, 'You successfully added this article to your "Favorites"')
    else:
        favorite.delete()
        messages.success(
            request, 'You successfully deleted this article from your "Favorites"')

    return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))


@login_required()
def favorite_articles(request):
    # View to see articles that are in 'Favorites'
    current_user = request.user
    favorites = Favorite.objects.select_related(
        'article').filter(owner=current_user).all()
    number_of_favorites = len(favorites)
    if number_of_favorites == 0:
        message_to_display = 'You have no favorite article'
        articles = None
    else:
        if number_of_favorites == 1:
            message_to_display = 'You have 1 favorite article'
        else:
            message_to_display = f'You have {number_of_favorites} favorite articles'
        articles_ids = [favorite.article.id for favorite in favorites]
        articles = Article.objects.\
            select_related('author').\
            prefetch_related('tags').\
            filter(pk__in=articles_ids).all()
        return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                               'articles': articles})


def recommended_articles(request):
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, 'We cannot recommend you any articles while you are not authenticated')
        return redirect('core:index')
    subscriptions = Subscription.objects.\
        select_related('subscribe_to').filter(subscriber=current_user).all()
    subscribed_to_authors = [
        subscription.subscribe_to for subscription in subscriptions]
    articles_in_subscriptions = Article.objects.prefetch_related('tags').filter(
        author__username__in=subscribed_to_authors).all()
    tags_in_subscriptions = [article.tags.all()
                             for article in articles_in_subscriptions]
    tag_objects = []
    for tag_list in tags_in_subscriptions:
        for tag in tag_list:
            if tag in tag_objects:
                continue
            else:
                tag_objects.append(tag)
    article_objects = list(Article.objects.select_related('author').
                           prefetch_related('tags').
                           filter(tags__in=tag_objects).order_by('-pub_date').all())
    articles = []
    for article in article_objects:
        if article in articles:
            continue
        else:
            articles.append(article)
    if len(articles) == 0:
        message_to_display = 'We cannot recommend you any articles as you are not subscribed to any authors'
    else:
        message_to_display = 'Here are the articles recommended for you'
    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})
