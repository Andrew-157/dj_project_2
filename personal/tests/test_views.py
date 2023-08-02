import os
import tempfile
from datetime import timedelta
from PIL import Image
from io import BytesIO
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import Article, SocialMedia, UserDescription,\
    FavoriteArticles, Reaction, Comment, UserReading, Subscription

from users.models import CustomUser


class PersonalPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.\
            create_user(username='User1',
                        email='user1@gmail.com',
                        password='34somepassword34')

        test_user_2 = CustomUser.objects.\
            create_user(username='User2',
                        email='user2@gmail.com',
                        password='34somepassword34')

        test_user_3 = CustomUser.objects.\
            create_user(username='User3',
                        email='user3@gmail.com',
                        password='34somepassword34')

        Subscription.objects.create(
            subscribe_to=test_user_1,
            subscriber=test_user_2
        )

        Subscription.objects.create(
            subscribe_to=test_user_1,
            subscriber=test_user_3
        )

    def test_correct_redirect_not_logged_user(self):
        response = self.client.get(reverse('personal:personal-page'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:personal-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/personal_page.html')

    def test_correct_objects_in_context(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:personal-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('subscribers' in response.context)

    def test_number_of_logged_user_subscribers_is_calculated_correctly_in_context(self):
        user = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:personal-page'))
        user_subscribers = Subscription.objects.filter(
            subscribe_to=user).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subscribers'], user_subscribers)


class SubscriptionsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.\
            create_user(username='User1',
                        email='user1@gmail.com',
                        password='34somepassword34')

        test_user_2 = CustomUser.objects.\
            create_user(username='User2',
                        email='user2@gmail.com',
                        password='34somepassword34')

        test_user_3 = CustomUser.objects.\
            create_user(username='User3',
                        email='user3@gmail.com',
                        password='34somepassword34')

        Subscription.objects.\
            create(subscribe_to=test_user_2,
                   subscriber=test_user_1)

        Subscription.objects.\
            create(subscribe_to=test_user_3,
                   subscriber=test_user_1)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:subscriptions-list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:subscriptions-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/subscriptions_list.html')

    def test_correct_objects_in_context(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:subscriptions-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('subscriptions' in response.context)

    def test_number_of_logged_user_subscriptions_calculated_correctly_in_context(self):
        user = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:subscriptions-list'))
        user_subscriptions = Subscription.objects.\
            filter(subscriber=user).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['subscriptions']), user_subscriptions)


class ArticlesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.\
            create_user(username='User1',
                        email='someone@gmail.com',
                        password='34somepassword34')

        Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        Article.objects.\
            create(title='Something2',
                   content='Cool content 2',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:articles-list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:articles-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/articles_list.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:articles-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.context)

    def test_number_of_articles_in_context_calculated_correctly_for_logged_user(self):
        user = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:articles-list'))
        number_of_user_articles = Article.objects.filter(author=user).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['articles']), number_of_user_articles)


class ArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')

        Article.objects.create(
            title='title',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:article-detail',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_article(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:article-detail',
                                           kwargs={'pk': 555678}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_user_that_does_not_own_article(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        article = Article.objects.get(title='title')
        response = self.client.get(reverse('personal:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 403)

    def test_return_correct_template_for_user_that_owns_article(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        article = Article.objects.get(title='title')
        response = self.client.get(reverse('personal:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/article_detail.html')

    def test_correct_objects_in_context_for_user_that_owns_article(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        article = Article.objects.get(title='title')
        response = self.client.get(reverse('personal:article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article' in response.context)


class PublishArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')

    def tearDown(self) -> None:
        try:
            os.remove('media/core/images/test_image.jpg')
        except FileNotFoundError:
            pass
        return super().tearDown()

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:publish-article'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:publish-article'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/publish_article.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:publish-article'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_redirect_if_not_valid_data_posted(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')

        response = self.client.post(reverse('personal:publish-article'),
                                    data={'title': 'Some random title',
                                          'content': 'Some random content',
                                          'image': 'Not image',
                                          'tags': 'some_tag, another_tag'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/publish_article.html')

    def test_correct_response_after_publishing_article(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'jpeg')
        image_file.seek(0)

        response = self.client.post(reverse('personal:publish-article'),
                                    data={'title': 'Some random title',
                                          'content': 'Some random content',
                                          'image': SimpleUploadedFile("test_image.jpg", image_file.read(),
                                                                      content_type="image/jpeg"),
                                          'tags': 'some_tag, another_tag'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:articles-list'))
        self.assertEqual(str(messages[0]),
                         'You successfully published new article')
        article = Article.objects.filter(title='Some random title').first()
        self.assertTrue(article)


class UpdateArticleThroughArticlesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')

        Article.objects.create(
            title='title',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def tearDown(self) -> None:
        try:
            os.remove('media/core/images/test_image.jpg')
        except FileNotFoundError:
            pass
        return super().tearDown()

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:update-article-list',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_movie_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-list',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_logged_user_who_does_not_own_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-list',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_for_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-list',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_article.html')

    def test_correct_objects_in_context_for_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-list',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue('send_post_to' in response.context)

    def test_correct_response_if_invalid_data_posted_by_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        response = self.client.post(reverse('personal:update-article-list',
                                            kwargs={'pk': article.id}),
                                    data={'title': article.title,
                                          'content': article.content,
                                          'image': SimpleUploadedFile("test_image.jpg", image_file.read(),
                                                                      content_type="image/jpeg")})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_article.html')

    def test_correct_response_to_user_who_owns_article_successfully_updated_it(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        response = self.client.post(reverse('personal:update-article-list',
                                            kwargs={'pk': article.id}),
                                    data={'title': 'New article title',
                                          'content': article.content,
                                          'image': SimpleUploadedFile("test_image.jpg", image_file.read(),
                                                                      content_type="image/jpeg"),
                                          'tags': 'some_tag'
                                          })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:articles-list'))
        self.assertEqual(str(messages[0]),
                         'You successfully updated your article')
        article = Article.objects.filter(title='New article title').first()
        self.assertTrue(article is not None)


class UpdateArticleThroughArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')

        Article.objects.create(
            title='title',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def tearDown(self) -> None:
        try:
            os.remove('media/core/images/test_image.jpg')
        except FileNotFoundError:
            pass
        return super().tearDown()

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:update-article-detail',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_movie_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-detail',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_logged_user_who_does_not_own_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_for_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_article.html')

    def test_correct_objects_in_context_for_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-article-detail',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue('send_post_to' in response.context)

    def test_correct_response_if_invalid_data_posted_by_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        response = self.client.post(reverse('personal:update-article-detail',
                                            kwargs={'pk': article.id}),
                                    data={'title': article.title,
                                          'content': article.content,
                                          'image': SimpleUploadedFile("test_image.jpg", image_file.read(),
                                                                      content_type="image/jpeg")})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_article.html')

    def test_correct_to_user_who_owns_article_successfully_updated_it(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        response = self.client.post(reverse('personal:update-article-detail',
                                            kwargs={'pk': article.id}),
                                    data={'title': 'New article title',
                                          'content': article.content,
                                          'image': SimpleUploadedFile("test_image.jpg", image_file.read(),
                                                                      content_type="image/jpeg"),
                                          'tags': 'some_tag'
                                          })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'personal:article-detail', kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully updated your article')
        article = Article.objects.filter(title='New article title').first()
        self.assertTrue(article is not None)


class DeleteArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')

        Article.objects.create(
            title='title',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-article',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_article_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-article',
                                            kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_logged_user_who_does_not_own_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 403)

    def test_redirect_after_successful_article_deletion_by_logged_user_who_owns_article(self):
        article = Article.objects.get(title='title')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:articles-list'))
        self.assertEqual(str(messages[0]),
                         'You successfully deleted your article')
        article = Article.objects.filter(title='title').first()
        self.assertTrue(article is None)


class AboutPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='someone@gmail.com')

        Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=78
        )

        SocialMedia.objects.create(
            user=test_user_1,
            link='https://github.com/',
            title='YB'
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:about-page'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:about-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/about_page.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:about-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('social_media_list' in response.context)
        self.assertTrue('description' in response.context)
        self.assertTrue('readings' in response.context)

    def test_readings_are_calculated_correctly_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:about-page'))
        number_of_readings = Article.objects.filter(
            author__username='User1').aggregate(Sum('times_read'))['times_read__sum']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['readings'], number_of_readings)

    def test_correct_length_of_social_media_links_is_returned_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:about-page'))
        number_of_social_media_objects = SocialMedia.objects.\
            filter(user__username='User1').count()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['social_media_list']),
                        number_of_social_media_objects)

    def test_correct_response_when_logged_user_posts_not_unique_link(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:about-page'),
                                    data={'link': 'https://github.com/',
                                          'title': 'TT'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/about_page.html')

    def test_correct_response_when_logged_user_posts_valid_link(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:about-page'),
                                    data={'link': 'https://www.youtube.com/',
                                          'title': 'YB'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(
            str(messages[0]), 'You successfully added new link to your social media')
        social_media_link = SocialMedia.objects.filter(
            link='https://www.youtube.com/').first()
        self.assertTrue(social_media_link is not None)


class DeleteSocialMediaViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        SocialMedia.objects.create(
            user=test_user_1,
            link='https://www.youtube.com/',
            title='YB'
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:social_media-delete',
                                           kwargs={'pk': 999}))
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_link(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:social_media-delete',
                                            kwargs={'pk': 675}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_logged_user_that_does_not_own_link(self):
        social_media_link = SocialMedia.objects.get(user__username='User1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:social_media-delete',
                                            kwargs={'pk': social_media_link.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_response_after_successful_deletion_of_link_by_logged_user(self):
        login = self.client.login(
            username='User1', password='34somepassword34')
        social_media_link = SocialMedia.objects.get(user__username='User1')
        response = self.client.post(reverse('personal:social_media-delete',
                                            kwargs={'pk': social_media_link.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted this social media link')
        social_media_link = SocialMedia.objects.filter(
            user__username='User1').first()
        self.assertTrue(social_media_link is None)


class PublishUserDescriptionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')
        UserDescription.objects.create(
            user=test_user_2,
            content='My user description.'
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:add-user-description'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_redirect_for_logged_with_description(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:add-user-description'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(str(messages[0]),
                         'You already have a description, you can either delete or update it')

    def test_view_uses_correct_template_for_logged_user_without_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:add-user-description'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/publish_description.html')

    def test_view_uses_correct_objects_in_context_for_logged_user_without_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:add-user-description'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_response_if_invalid_data_posted_by_logged_user_without_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:add-user-description'),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/publish_description.html')

    def test_correct_response_if_valid_data_posted_by_user_without_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:add-user-description'),
                                    data={'content': 'My user description.'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(
            str(messages[0]), 'You successfully published your description')
        user_description = UserDescription.objects.filter(
            user__username='User1').first()
        self.assertTrue(user_description is not None)


class UpdateUserDescriptionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        UserDescription.objects.create(
            user=test_user_1,
            content='My user description.'
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:update-user-description'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_redirect_for_logged_user_without_description(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-user-description'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(str(messages[0]),
                         'You cannot update your description, as you do not have one')

    def test_view_uses_correct_template_for_logged_user_with_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-user-description'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_description.html')

    def test_view_uses_correct_objects_in_context_for_logged_user_with_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:update-user-description'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_response_if_logged_user_with_description_posts_invalid_data(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:update-user-description'),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/update_description.html')

    def test_correct_response_if_logged_user_with_description_posts_valid_data(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:update-user-description'),
                                    data={'content': 'My new user description.'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(str(messages[0]),
                         'You successfully updated your description')
        user_description = UserDescription.objects.filter(
            user__username='User1').first()
        self.assertEqual(user_description.content, 'My new user description.')


class DeleteUserDescriptionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        UserDescription.objects.create(
            user=test_user_1,
            content='My user description.'
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-user-description'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_redirect_for_logged_user_without_description(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('personal:delete-user-description'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(str(messages[0]),
                         'You do not have a description, you cannot delete it')

    def test_correct_response_after_deletion_of_description_by_logged_user_with_description(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('personal:delete-user-description'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:about-page'))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted your description')
        user_description = UserDescription.objects.filter(
            user__username='User1').first()
        self.assertTrue(user_description is None)


class ReadingHistoryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   password='34somepassword34',
                                                   email='user1@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=78
        )

        UserReading.objects.create(
            user=test_user,
            article=article_1,
            date_read=timezone.now()
        )

        UserReading.objects.create(
            user=test_user,
            article=article_2,
            date_read=timezone.now() + timedelta(minutes=10)
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:reading-history'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:reading-history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/reading_history.html')

    def test_view_has_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:reading-history'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('user_readings' in response.context)

    def test_view_calculates_user_readings_correctly_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:reading-history'))
        number_of_user_readings = UserReading.objects.\
            filter(user__username='User1').count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['user_readings']), number_of_user_readings)


class ClearReadingHistoryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   password='34somepassword34',
                                                   email='user1@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=78
        )

        UserReading.objects.create(
            user=test_user,
            article=article_1,
            date_read=timezone.now()
        )

        UserReading.objects.create(
            user=test_user,
            article=article_2,
            date_read=timezone.now() + timedelta(minutes=10)
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:clear-reading-history'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_after_clearing_history_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:clear-reading-history'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:reading-history'))
        self.assertEqual(str(messages[0]),
                         'You successfully cleared your reading history')
        user_readings = UserReading.objects.filter(
            user__username='User1').count()
        self.assertEqual(user_readings, 0)


class DeleteUserReadingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        UserReading.objects.create(
            user=test_user_1,
            article=article,
            date_read=timezone.now()
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-reading',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_to_nonexistent_user_reading_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-reading',
                                            kwargs={'pk': 333}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_logged_user_that_does_not_own_reading(self):
        user_reading = UserReading.objects.get(user__username='User1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-reading',
                                            kwargs={'pk': user_reading.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_response_after_logged_user_successfully_deleted_their_user_reading(self):
        user_reading = UserReading.objects.get(user__username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-reading',
                                            kwargs={'pk': user_reading.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:reading-history'))
        self.assertEqual(str(messages[0]), 'You successfully deleted info about reading this article\
        from your reading history')
        user_reading = UserReading.objects.filter(
            user__username='User1').first()
        self.assertTrue(user_reading is None)


class LikedArticlesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=65
        )

        Reaction.objects.create(
            value=1,
            user=test_user_1,
            article=article_1
        )

        Reaction.objects.create(
            value=1,
            user=test_user_1,
            article=article_2
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:liked-articles'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:liked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/liked_articles.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:liked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reaction_objects' in response.context)

    def test_view_calculates_correctly_number_of_liked_articles_for_logged_user(self):
        liked_articles_number = Reaction.objects.filter(
            Q(value=1) & Q(user__username='User1')).count()
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:liked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reaction_objects']),
                         liked_articles_number)


class DislikedArticlesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=65
        )

        Reaction.objects.create(
            value=-1,
            user=test_user_1,
            article=article_1
        )

        Reaction.objects.create(
            value=-1,
            user=test_user_1,
            article=article_2
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:disliked-articles'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:disliked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/disliked_articles.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:disliked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reaction_objects' in response.context)

    def test_view_calculates_correctly_number_of_disliked_articles_for_logged_user(self):
        liked_articles_number = Reaction.objects.filter(
            Q(value=-1) & Q(user__username='User1')).count()
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:disliked-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reaction_objects']),
                         liked_articles_number)


class ClearLikesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.\
            create_user(username='User1',
                        password='34somepassword34',
                        email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=65
        )

        Reaction.objects.create(
            value=1,
            user=test_user_1,
            article=article_1
        )

        Reaction.objects.create(
            value=1,
            user=test_user_1,
            article=article_2
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:clear-likes'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_after_successful_clearing_of_likes_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:clear-likes'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:liked-articles'))
        self.assertEqual(str(messages[0]),
                         'You successfully cleared your likes')
        reactions = Reaction.objects.filter(user__username='User1').count()
        self.assertEqual(reactions, 0)


class ClearDislikesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.\
            create_user(username='User1',
                        password='34somepassword34',
                        email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_2,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=65
        )

        Reaction.objects.create(
            value=-1,
            user=test_user_1,
            article=article_1
        )

        Reaction.objects.create(
            value=-1,
            user=test_user_1,
            article=article_2
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:clear-dislikes'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_redirect_after_successful_clearing_of_dislikes_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:clear-dislikes'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:disliked-articles'))
        self.assertEqual(str(messages[0]),
                         'You successfully cleared your dislikes')
        reactions = Reaction.objects.filter(user__username='User1').count()
        self.assertEqual(reactions, 0)


class DeleteLikeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        article = Article.objects.\
            create(
                title='title1',
                content='Cool content 1',
                author=test_user_2,
                image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                times_read=56
            )

        Reaction.objects.create(
            value=1,
            user=test_user_1,
            article=article
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-like',
                                           kwargs={'pk': 456}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_to_logged_user_that_does_not_own_like(self):
        like = Reaction.objects.get(user__username='User1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-like',
                                            kwargs={'pk': like.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_response_for_nonexistent_like_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-like',
                                            kwargs={'pk': 889}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_after_like_deletion_by_logged_user_that_owns_like(self):
        like = Reaction.objects.get(user__username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-like',
                                            kwargs={'pk': like.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:liked-articles'))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted one like reaction')
        reaction = Reaction.objects.filter(user__username='User1').first()
        self.assertTrue(reaction is None)


class DeleteDislikeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        article = Article.objects.\
            create(
                title='title1',
                content='Cool content 1',
                author=test_user_2,
                image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                times_read=56
            )

        Reaction.objects.create(
            value=-1,
            user=test_user_1,
            article=article
        )

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-dislike',
                                           kwargs={'pk': 456}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_to_logged_user_that_does_not_own_dislike(self):
        dislike = Reaction.objects.get(user__username='User1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-dislike',
                                            kwargs={'pk': dislike.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_response_for_nonexistent_dislike_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-like',
                                            kwargs={'pk': 889}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_after_dislike_deletion_by_logged_user_that_owns_dislike(self):
        dislike = Reaction.objects.get(user__username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-dislike',
                                            kwargs={'pk': dislike.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:disliked-articles'))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted one dislike reaction')
        reaction = Reaction.objects.filter(user__username='User1').first()
        self.assertTrue(reaction is None)


class FavoriteArticlesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user@gmail.com')
        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=65
        )

        fav_obj = FavoriteArticles.objects.create(user=test_user_1)

        fav_obj.articles.add(article_1)
        fav_obj.articles.add(article_2)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/favorite_articles.html')

    def test_correct_objects_in_context_for_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.context)

    def test_view_correctly_calculates_favorite_articles_for_logged_user(self):
        fav_obj = FavoriteArticles.objects.get(user__username='User1')
        number_of_fav_articles = len(fav_obj.articles.all())
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['articles']), number_of_fav_articles)

    def test_correct_template_for_logged_user_without_fav_obj(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/favorite_articles.html')

    def test_correct_objects_for_logged_user_without_fav_obj(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.context)

    def test_view_correct_object_type_in_context_for_logged_user_without_fav_object(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('personal:favorite-articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['articles'], None)


class DeleteFavoriteArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        fav_obj = FavoriteArticles.objects.create(user=test_user_1)

        fav_obj.articles.add(article_1)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-favorite-article',
                                           kwargs={'pk': 698}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_to_nonexistent_article_for_logged_user(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-favorite-article',
                                            kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_existent_article_for_logged_user_without_fav_object(self):
        article = Article.objects.get(title='title1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-favorite-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:favorite-articles'))
        self.assertEqual(str(messages[0]),
                         'You do not have any articles to remove from Favorites')

    def test_correct_response_for_logged_user_with_existent_article_that_is_not_in_favorites(self):
        article = Article.objects.get(title='title2')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-favorite-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:favorite-articles'))
        self.assertEqual(str(messages[0]),
                         'This article is not in your Favorites')

    def test_correct_response_after_successful_removal_of_article_by_logged_user(self):
        article = Article.objects.get(title='title1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:delete-favorite-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:favorite-articles'))
        self.assertEqual(str(messages[0]),
                         'You successfully removed an article from your Favorites')
        fav_obj = FavoriteArticles.objects.filter(
            user__username='User1').first()
        article = Article.objects.filter(title='title1').first()
        self.assertTrue(article not in fav_obj.articles.all())


class ClearFavoritesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        article_1 = Article.objects.create(
            title='title1',
            content='Cool content 1',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        article_2 = Article.objects.create(
            title='title2',
            content='Cool content 2',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=56
        )

        fav_obj = FavoriteArticles.objects.create(user=test_user_1)

        fav_obj.articles.add(article_1)

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('personal:delete-favorite-article',
                                           kwargs={'pk': 698}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_after_clearing_favorites_by_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:clear-favorites'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:favorite-articles'))
        self.assertEqual(
            str(messages[0]), 'All your Favorites were successfully deleted')
        fav_obj = FavoriteArticles.objects.filter(
            user__username='User1').first()
        self.assertEqual(len(fav_obj.articles.all()), 0)

    def test_correct_response_after_clearing_favorites_by_logged_user_without_fav_object(self):
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('personal:clear-favorites'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('personal:favorite-articles'))
        self.assertEqual(
            str(messages[0]), 'All your Favorites were successfully deleted')
