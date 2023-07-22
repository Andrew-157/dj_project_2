from datetime import timedelta
from django.db.models.query_utils import Q
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from taggit.models import Tag, TaggedItem
from core.models import Article, Subscription, FavoriteArticles, UserReading, Reaction


class IndexView(View):
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        tagged_items_ids = [t.tag_id for t in TaggedItem.objects.all()]
        tags = Tag.objects.filter(
            id__in=tagged_items_ids).all().order_by('name')
        return render(request, self.template_name, {'tags': tags})

# class IndexView(View):
#     """
#     View for showing Index Page of site
#     and recommending articles
#     """
#     template_name = 'core/index.html'
#     min_times_read = 5
#     past_reference_date = timezone.now() - timedelta(days=7)
#     min_length_of_tags_list = 2
#     min_length_of_articles_list = 5

#     def get_most_popular_tags(self, articles: Article):
#         # this view returns tags that most popular
#         # articles published in recent time contain
#         tags = []
#         for article in articles:
#             for tag in article.tags.all():
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         return tags

#     def get_most_popular_articles_in_recent_time(self):
#         # most popular are those that have
#         # times_read attribute greater than particular value
#         # defined in the class, and that were published not later than
#         # reference date defined in the class
#         articles = Article.objects.\
#             select_related('author').\
#             prefetch_related('tags').\
#             filter(Q(times_read__gt=self.min_times_read) &
#                    Q(pub_date__gt=self.past_reference_date)).\
#             order_by('-times_read').all()
#         return list(articles)

#     def get_user_subscriptions(self, user):
#         # this view returns authors current user is subscribed to
#         subscriptions = Subscription.objects.filter(subscriber=user).all()
#         return [s.subscribe_to.id for s in subscriptions]

#     def get_latest_articles_from_subscriptions(self, user_subs):
#         # this method returns articles published by authors,
#         # that the user is subscribed to, published not later than
#         # reference date defined in the class
#         articles = Article.objects.\
#             select_related('author').\
#             prefetch_related('tags').\
#             filter(
#                 Q(author__id__in=user_subs) &
#                 Q(pub_date__gt=self.past_reference_date)
#             ).all()
#         return list(articles)

#     def get_tags_from_favorites(self, user):
#         # this view returns tags of articles ,marked as favorites
#         # by current user
#         favorite_obj = FavoriteArticles.objects.\
#             select_related('user').prefetch_related(
#                 'articles').filter(user=user).first()
#         if not favorite_obj:
#             return None
#         articles = favorite_obj.articles.prefetch_related('tags').all()
#         tags = []
#         for article in articles:
#             for tag in article.tags.all():
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         return tags

#     def get_tags_from_liked_articles(self, user):
#         # this view returns tags of articles, liked by current user
#         user_likes = Reaction.objects.\
#             select_related('article').\
#             filter(
#                 Q(user=user) &
#                 Q(value=1)
#             ).all()
#         articles = [ul.article for ul in user_likes]
#         tags = []
#         for article in articles:
#             for tag in article.tags.all():
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         return tags

#     def get_tags_from_reading_history(self, user):
#         # this view returns tags of articles
#         # user read
#         user_readings = UserReading.objects.\
#             select_related('article').\
#             filter(user=user).all()
#         articles = [ur.article for ur in user_readings]
#         tags = []
#         for article in articles:
#             for tag in article.tags.all():
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         return tags

#     def get_recommended_tags(self, user):
#         # this view gathers all tags based
#         # on likes, favorites, reading history using
#         # another class methods, this view leaves only unique tags
#         tags = []
#         tags_favorites = self.get_tags_from_favorites(user)
#         tags_liked = self.get_tags_from_liked_articles(user)
#         tags_history = self.get_tags_from_reading_history(user)
#         if tags_favorites:
#             for tag in tags_favorites:
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         if tags_liked:
#             for tag in tags_liked:
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         if tags_history:
#             for tag in tags_history:
#                 if not tag in tags:
#                     tags.append(tag)
#                 else:
#                     continue
#         # if gathered amount of tags is too small
#         # this view takes most popular tags through another class method
#         if len(tags) < self.min_length_of_tags_list:
#             popular_articles = self.get_most_popular_articles_in_recent_time()
#             popular_tags = self.get_most_popular_tags(popular_articles)
#             tags += popular_tags
#         return tags

#     def get_recommended_articles(self, user, tags):
#         # this view gathers articles based on tags
#         # passed as an argument, this view leaves only unique articles
#         articles = []
#         user_subs = self.get_user_subscriptions(user)
#         latest_articles_from_subscriptions = self.get_latest_articles_from_subscriptions(
#             user_subs)
#         articles += latest_articles_from_subscriptions
#         for tag in tags:
#             article = Article.objects.\
#                 select_related('author').\
#                 prefetch_related('tags').\
#                 filter(tags=tag).first()
#             if not article in articles:
#                 articles.append(article)
#             else:
#                 continue
#         # if the amount of articles is too small,
#         # this view takes most popular articles through another class method
#         if len(articles) < self.min_length_of_articles_list:
#             popular_articles = self.get_most_popular_articles_in_recent_time()
#             articles += popular_articles
#         return articles

#     def get(self, request, *args, **kwargs):
#         current_user = request.user
#         if not current_user.is_authenticated:
#             # for unauthenticated user we get only most popular articles and tags
#             # as recommended
#             articles = self.get_most_popular_articles_in_recent_time()
#             tags = self.get_most_popular_tags(articles)
#         else:
#             tags = self.get_recommended_tags(current_user)
#             articles = self.get_recommended_articles(current_user, tags)
#         return render(request, self.template_name, {'articles': articles,
#                                                     'tags': tags})


def error_404_handler(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_403_handler(request, exception):
    return render(request, 'errors/403.html', status=403)
