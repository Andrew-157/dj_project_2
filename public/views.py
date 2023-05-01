from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.db.models.query_utils import Q
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from taggit.models import Tag
from core.models import CustomUser, Article, Reaction, Comment, Subscription, SocialMedia, UserReadings, Favorite
from .forms import CommentArticleForm


def public_article(request, article_id):
    current_user = request.user
    user_reaction_message = None
    likes = 0
    dislikes = 0
    comments = None
    in_favorites = 'Add to "Favorites" '
    article = Article.objects.select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    if current_user.is_authenticated:
        user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                    Q(article=article)).first()
        if not user_readings:
            user_readings = UserReadings(
                user=current_user,
                article=article,
                times_read=1
            )
            user_readings.save()
        else:
            user_readings.times_read += 1
            user_readings.save()
        article.times_read += 1
        article.save()
        user_reaction = Reaction.objects.filter(
            Q(article=article)
            &
            Q(reaction_owner=current_user)
        ).first()
        if user_reaction:
            if user_reaction.value == -1:
                user_reaction_message = 'You disliked this article'
            if user_reaction.value == 1:
                user_reaction_message = 'You liked this article'
        favorite = Favorite.objects.filter(
            Q(owner=current_user) &
            Q(article=article)
        ).first()
        if favorite:
            in_favorites = 'Delete from "Favorites" '
    article_reactions = Reaction.objects.filter(article=article).all()
    if article_reactions:
        likes = article_reactions.filter(value=1).count()
        dislikes = article_reactions.filter(value=-1).count()
    article_comments = Comment.objects.filter(
        article=article).select_related('commentator').all()
    if article_comments:
        comments = article_comments
    return render(request, 'public/public_article.html', {'article': article,
                                                          'user_reaction_message': user_reaction_message,
                                                          'likes': likes,
                                                          'dislikes': dislikes,
                                                          'comments': comments,
                                                          'in_favorites': in_favorites})


def like_article(request, article_id):
    current_user = request.user
    if not current_user.is_authenticated:
        # here login_required decorator is not applied
        # because we want user to return to the public page of the article
        # with message that they need to be authenticated to leave a reaction
        messages.info(
            request, 'To leave a reaction, please, become an authenticated user')
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        # this if statement ensures that view works properly as
        # we check if user read an article and does not try to hit
        # url for likes directly
        messages.warning(
            request, "Do not try to leave like without reading an article")
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    else:
        # when this view redirects you back to the public page of the article
        # this does not count as user read
        user_readings.times_read -= 1
        user_readings.save()
    # when this view redirects you back to the public page of the article
    # this does not count as article was read one more time
    # so article.times_read only increases
    # when you hit public-article url
    article.times_read -= 1
    article.save()
    reaction = Reaction.objects.filter(
        Q(article=article)
        &
        Q(reaction_owner=current_user)
    ).first()
    if not reaction:
        reaction = Reaction(
            value=1, reaction_owner=current_user, article=article)
        reaction.save()
    else:
        if reaction.value == -1:
            reaction.value = 1
            reaction.save()
        elif reaction.value == 1:
            reaction.delete()

    return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))


def dislike_article(request, article_id):
    # this view is basically the same as like_article
    # but with the opposite values
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(request, 'To leave a reaction, please, sign in')
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'core/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        messages.warning(
            request, "Do not try to leave dislike without reading an article")
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    else:
        user_readings.times_read -= 1
        user_readings.save()
    article.times_read -= 1
    article.save()
    reaction = Reaction.objects.filter(
        Q(article=article)
        &
        Q(reaction_owner=current_user)
    ).first()
    if not reaction:
        reaction = Reaction(
            value=-1, reaction_owner=current_user, article=article)
        reaction.save()
    else:
        if reaction.value == 1:
            reaction.value = -1
            reaction.save()
        elif reaction.value == -1:
            reaction.delete()

    return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))


def comment_article(request, article_id):
    current_user = request.user
    if not current_user.is_authenticated:
        # here login_required decorator is not applied
        # because we want user to return to the public page of the article
        # with message that they need to be authenticated to leave a comment
        messages.info(
            request, 'To leave a comment, please, become an authenticated user')
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).\
        select_related('author').first()
    if not article:
        return render(request, 'core/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        messages.warning(
            request, "Do not try to leave comment without reading an article")
        return HttpResponseRedirect(reverse('public:public-article', args=(article_id,)))
    if request.method == 'POST':
        article.times_read -= 1
        article.save()
        user_readings.times_read -= 1
        user_readings.save()
        form = CommentArticleForm(request.POST)
        if form.is_valid():
            form.instance.commentator = current_user
            form.instance.article = article
            if article.author == current_user:
                form.instance.is_author = True
            form.save()
            messages.success(
                request, 'You successfully left a comment on this article')
            return HttpResponseRedirect(reverse('public:public-article', args=(article_id, )))
    form = CommentArticleForm()
    return render(request, 'public/comment_article.html', {'form': form, 'article': article})


def find_articles_through_tag(request, tag):
    tag_object = Tag.objects.filter(slug=tag).first()
    if not tag_object:
        return render(request, 'core/nonexistent.html')
    articles = Article.objects.prefetch_related('tags').\
        filter(tags=tag_object).order_by('-times_read').all()
    number_of_articles = len(articles)
    if number_of_articles < 0:
        message_to_display = f'No articles were found with this tag #{tag_object}'
    if number_of_articles == 1:
        message_to_display = f'One article was found with this tag #{tag_object}'
    if number_of_articles > 1:
        message_to_display = f'{number_of_articles} articles were found with this tag #{tag_object}'
    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})


def author_page(request, author):
    current_user = request.user
    subscription_status = 'Subscribe'
    total_readings = None
    is_owner = False
    author_object = CustomUser.objects.filter(username=author).first()
    if not author_object:
        return render(request, 'core/nonexistent.html')
    if current_user == author_object:
        is_owner = True
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        order_by('-pub_date').\
        filter(author=author_object).all()
    if articles:
        total_readings = sum(articles.values_list('times_read', flat=True))
    if current_user.is_authenticated:
        subscription = Subscription.objects.filter(
            Q(subscriber=current_user) &
            Q(subscribe_to=author_object)
        ).first()
        # this subscription status is shown
        # as button, so if user is subscribed
        # they see unsubscribe button and vice versa
        if subscription:
            subscription_status = 'Unsubscribe'
        else:
            subscription_status = 'Subscribe'
    subscribers = Subscription.objects.filter(
        subscribe_to=author_object).count()
    social_media = SocialMedia.objects.filter(user=author_object).all()
    return render(request, 'public/author_page.html', {'author': author_object,
                                                       'articles': articles,
                                                       'total_readings': total_readings,
                                                       'number_of_articles': len(articles),
                                                       'subscribers': subscribers,
                                                       'subscription_status': subscription_status,
                                                       'is_owner': is_owner,
                                                       'social_media': social_media})


def subscribe_request(request, author):
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, 'To subscribe you need to be an authenticated user')
        return HttpResponseRedirect(reverse('public:author-page', args=(author,)))
    author_object = CustomUser.objects.filter(username=author).first()
    if not author_object:
        return render(request, 'core/nonexistent.html')
    if current_user == author_object:
        messages.info(request, 'You cannot subscribe to yourself')
        return HttpResponseRedirect(reverse('public:author-page', args=(author,)))
    subscription = Subscription.objects.filter(
        Q(subscriber=current_user) &
        Q(subscribe_to=author_object)
    ).first()
    if not subscription:
        subscription = Subscription(
            subscriber=current_user,
            subscribe_to=author_object
        )
        subscription.save()
        messages.success(request, 'You successfully subscribed to this author')
        return HttpResponseRedirect(reverse('public:author-page', args=(author, )))
    else:
        subscription.delete()
        messages.success(
            request, 'You successfully unsubscribed from this author')
        return HttpResponseRedirect(reverse('public:author-page', args=(author, )))


def search_articles(request):
    search_string = request.POST['search_string']
    if not search_string:
        return render(request, 'core/nonexistent.html')
    if len(search_string) == 1 and search_string[0] == '#':
        return render(request, 'core/nonexistent.html')
    if search_string[0] == '#':
        tag = search_string[1:]
        return HttpResponseRedirect(reverse('public:tag-article', args=(tag, )))
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(Q(title__icontains=search_string) |
               Q(author__username__icontains=search_string)).\
        order_by('-times_read').\
        all()
    number_of_articles = len(articles)
    if number_of_articles == 0:
        message_to_display = f"No articles were found that contain ---{search_string}--- \
            in author's name or title"
    elif number_of_articles == 1:
        message_to_display = f"1 article was found that contains ---{search_string}--- \
            in author's name or title"
    else:
        message_to_display = f"{number_of_articles} articles were found that contain ---{search_string}---\
            in author's name or title"

    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})


def popular_articles(request):
    past_date = timezone.now() - timedelta(days=7)
    future_date = timezone.now() + timedelta(days=7)
    articles = Article.objects.select_related('author').\
        filter(
        Q(pub_date__gt=past_date) &
        Q(pub_date__lt=future_date) &
        Q(times_read__gt=50)
    ).order_by('-times_read').all()[:10]
    message_to_display = 'You are seeing the most popular articles in recent time'
    return render(request, 'public/public_articles.html', {'message_to_display': message_to_display,
                                                           'articles': articles})
