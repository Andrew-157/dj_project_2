import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from django.db.models import Sum
from django.db.models.query_utils import Q

from core.models import Article, SocialMedia, UserDescription,\
    FavoriteArticles, Reaction, Comment, UserReading, Subscription

from users.models import CustomUser


class AboutPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   email='user1@gmail.com',
                                                   password='34somepassword34')

        Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        Article.objects.\
            create(title='Something2',
                   content='Cool content 2',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=98)

    def test_view_uses_correct_template(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:about-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/about_page.html')

    def test_correct_objects_in_context(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:about-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('description' in response.context)
        self.assertTrue('social_media_list' in response.context)
        self.assertTrue('author' in response.context)
        self.assertTrue('readings' in response.context)

    def test_number_of_author_readings_calculated_correctly(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:about-page',
                                           kwargs={'pk': author.id}))
        number_of_readings = Article.objects.filter(
            author=author).aggregate(Sum('times_read'))['times_read__sum']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['readings'], number_of_readings)

    def test_correct_response_to_nonexistent_author(self):
        response = self.client.get(reverse('public:about-page',
                                           kwargs={'pk': 8789}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/nonexistent.html')


class ArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')
        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     email='user3@gmail.com',
                                                     password='34somepassword34')

        Subscription.objects.create(subscribe_to=test_user_1,
                                    subscriber=test_user_2)

        Subscription.objects.create(subscribe_to=test_user_1,
                                    subscriber=test_user_3)

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user_1,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        Reaction.objects.create(user=test_user_2,
                                value=1,
                                article=article)

        Reaction.objects.create(user=test_user_3,
                                value=-1,
                                article=article)

        fav_obj = FavoriteArticles.objects.create(user=test_user_2)
        fav_obj.articles.add(article)

    def test_view_uses_correct_template(self):
        article = Article.objects.get(title='Something1')
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/article_detail.html')

    def test_correct_objects_in_context(self):
        article = Article.objects.get(title='Something1')
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article' in response.context)
        self.assertTrue('favorite_status' in response.context)
        self.assertTrue('show_content' in response.context)
        self.assertTrue('reaction_status' in response.context)
        self.assertTrue('likes' in response.context)
        self.assertTrue('dislikes' in response.context)
        self.assertTrue('subscribers' in response.context)

    def test_view_calculates_correctly_objects_in_context(self):
        article = Article.objects.get(title='Something1')
        author = CustomUser.objects.get(username='User1')
        number_of_subscribers = Subscription.objects.filter(
            subscribe_to=author).count()
        number_of_likes = Reaction.objects.filter(
            Q(article=article) & Q(value=1)).count()
        number_of_dislikes = Reaction.objects.filter(
            Q(article=article) & Q(value=-1)).count()
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['subscribers'], number_of_subscribers)
        self.assertEqual(response.context['likes'], number_of_likes)
        self.assertEqual(response.context['dislikes'], number_of_dislikes)

    def test_correct_subscription_status_shown_for_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subscription_status'],
                         'Unsubscribe')

    def test_correct_reaction_status_for_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reaction_status'],
                         'You liked this article')

    def test_favorite_status_for_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['favorite_status'],
                         'Remove from Favorites')

    def test_show_content_changes_to_true_when_post_method(self):
        article = Article.objects.get(title='Something1')
        response = self.client.post(reverse('public:article-detail',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_content'])

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.post(reverse('public:article-detail',
                                            kwargs={'pk': 888}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/nonexistent.html')


class CommentsByArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   email='user1@gmail.com',
                                                   password='34somepassword34')

        Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

    def test_view_uses_correct_template(self):
        article = Article.objects.get(title='Something1')
        response = self.client.get(reverse('public:article-comments',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/comments_by_article.html')

    def test_correct_objects_in_context(self):
        article = Article.objects.get(title='Something1')
        response = self.client.get(reverse('public:article-comments',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comments' in response.context)
        self.assertTrue('article' in response.context)

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.get(reverse('public:article-comments',
                                           kwargs={'pk': 4567}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/nonexistent.html')
