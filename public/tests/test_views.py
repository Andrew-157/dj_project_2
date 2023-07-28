import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
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


class AddRemoveFavoriteArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user_3,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        fav_obj_1 = FavoriteArticles.objects.create(user=test_user_1)
        fav_obj_2 = FavoriteArticles.objects.create(user=test_user_2)

        fav_obj_1.articles.add(article)

    def test_correct_response_to_nonexistent_article(self):
        response = self.client.post(reverse('public:manage-favorites',
                                            kwargs={'pk': 345}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_not_logged_user(self):
        article = Article.objects.get(title='Something1')
        response = self.client.post(reverse('public:manage-favorites',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'Please, become an authenticated user to add this article to your Favorites')

    def test_correct_response_to_logged_user_without_fav_obj(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User3',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:manage-favorites',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully added this article to your Favorites')
        fav_obj = FavoriteArticles.objects.filter(
            user__username='User3').first()
        article = Article.objects.filter(title='Something1').first()
        self.assertTrue(article in fav_obj.articles.all())

    def test_correct_response_to_logged_user_with_fav_object_without_article(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:manage-favorites',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully added this article to your Favorites')
        fav_obj = FavoriteArticles.objects.filter(
            user__username='User2').first()
        article = Article.objects.filter(title='Something1').first()
        self.assertTrue(article in fav_obj.articles.all())

    def test_correct_response_to_logged_user_with_fav_object_with_article(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:manage-favorites',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully removed this article from your Favorites')
        fav_obj = FavoriteArticles.objects.filter(
            user__username='User1').first()
        article = Article.objects.filter(title='Something1')
        self.assertTrue(article not in fav_obj.articles.all())


class LeaveLikeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user_3,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        reaction_1 = Reaction.objects.create(article=article,
                                             user=test_user_1,
                                             value=1)

        reaction_2 = Reaction.objects.create(article=article,
                                             user=test_user_2,
                                             value=-1)

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.post(reverse('public:like-article',
                                            kwargs={'pk': 888}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_not_logged_user(self):
        article = Article.objects.get(title='Something1')
        response = self.client.post(reverse('public:like-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot leave like while you are not authenticated')

    def test_correct_response_to_logged_user_without_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User3',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:like-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User3').first()
        self.assertTrue(reaction is not None)
        self.assertEqual(reaction.value, 1)

    def test_correct_response_to_logged_user_with_dislike_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:like-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User2').first()
        self.assertTrue(reaction is not None)
        self.assertEqual(reaction.value, 1)

    def test_correct_response_to_logged_user_with_like_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:like-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User1').first()
        self.assertTrue(reaction is None)


class LeaveDislikeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user_3,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        reaction_1 = Reaction.objects.create(article=article,
                                             user=test_user_1,
                                             value=-1)

        reaction_2 = Reaction.objects.create(article=article,
                                             user=test_user_2,
                                             value=1)

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.post(reverse('public:dislike-article',
                                            kwargs={'pk': 888}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_not_logged_user(self):
        article = Article.objects.get(title='Something1')
        response = self.client.post(reverse('public:dislike-article',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot leave dislike while you are not authenticated')

    def test_correct_response_to_logged_user_without_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User3',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:dislike-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User3').first()
        self.assertTrue(reaction is not None)
        self.assertEqual(reaction.value, -1)

    def test_correct_response_to_logged_user_with_like_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:dislike-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User2').first()
        self.assertTrue(reaction is not None)
        self.assertEqual(reaction.value, -1)

    def test_correct_response_to_logged_user_with_dislike_reaction(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:dislike-article',
                                            kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        reaction = Reaction.objects.filter(user__username='User1').first()
        self.assertTrue(reaction is None)


class CommentArticleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   password='34somepassword34',
                                                   email='user1@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.get(reverse('public:comment-article',
                                           kwargs={'pk': 976}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_not_logged_user(self):
        article = Article.objects.get(title='Something1')
        response = self.client.get(reverse('public:comment-article',
                                           kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-comments',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'To leave a comment on this article, please become an authenticated user')

    def test_view_uses_correct_template_for_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:comment-article',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/comment_article.html')

    def test_view_uses_correct_objects_in_context_for_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:comment-article',
                                           kwargs={'pk': article.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article' in response.context)
        self.assertTrue('form' in response.context)

    def test_correct_response_for_logged_user_posting_invalid_data(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:comment-article',
                                            kwargs={'pk': article.id}),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/comment_article.html')

    def test_correct_response_after_posting_valid_data_by_logged_user(self):
        article = Article.objects.get(title='Something1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:comment-article',
                                            kwargs={'pk': article.id}),
                                    data={'content': 'Cool article'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-comments',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully published a comment on this article')
        comment = Comment.objects.filter(user__username='User1').first()
        self.assertTrue(comment is not None)


class DeleteCommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   password='34somepassword34',
                                                   email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        Comment.objects.create(
            user=test_user,
            article=article,
            content='Content'
        )

    def test_correct_response_to_not_logged_user(self):
        response = self.client.post(reverse('public:delete-comment',
                                            kwargs={'pk': 955}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_comment_to_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:delete-comment',
                                            kwargs={'pk': 888}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_logged_user_that_does_not_own_comment(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:delete-comment',
                                            kwargs={'pk': comment.id}))
        self.assertEqual(response.status_code, 403)

    def test_correct_response_after_successful_comment_deletion_be_logged_user(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:delete-comment',
                                            kwargs={'pk': comment.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-comments',
                                               kwargs={'pk': comment.article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully deleted your comment on this article')
        comment = Comment.objects.filter(user__username='User1').first()
        self.assertTrue(comment is None)


class UpdateCommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = CustomUser.objects.create_user(username='User1',
                                                   password='34somepassword34',
                                                   email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        article = Article.objects.\
            create(title='Something1',
                   content='Cool content 1',
                   author=test_user,
                   image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                   times_read=45)

        Comment.objects.create(
            user=test_user,
            article=article,
            content='Content'
        )

    def test_correct_response_to_not_logged_user(self):
        response = self.client.get(reverse('public:update-comment',
                                           kwargs={'pk': 955}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_correct_response_for_nonexistent_comment_to_logged_user(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:update-comment',
                                           kwargs={'pk': 888}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_to_logged_user_that_does_not_own_comment(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:update-comment',
                                           kwargs={'pk': comment.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template_for_logged_user_that_owns_comment(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:update-comment',
                                           kwargs={'pk': comment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/update_comment.html')

    def test_view_uses_correct_objects_in_context_for_logged_user_that_owns_comment(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:update-comment',
                                           kwargs={'pk': comment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comment' in response.context)
        self.assertTrue('article' in response.context)
        self.assertTrue('form' in response.context)

    def test_correct_response_when_logged_user_that_owns_comment_posts_invalid_data(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:update-comment',
                                            kwargs={'pk': comment.id}),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/update_comment.html')

    def test_correct_response_after_successful_updating_of_comment_by_logged_user(self):
        comment = Comment.objects.get(content='Content')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:update-comment',
                                            kwargs={'pk': comment.id}),
                                    data={'content': 'New content'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-comments',
                                               kwargs={'pk': comment.article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully updated your comment on this article')
        comment = Comment.objects.filter(user__username='User1').first()
        self.assertTrue(comment is not None)
        self.assertEqual(comment.content, 'New content')


class SubscribeUnsubscribeThroughArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')

        Article.objects.create(
            title='Title',
            content='Cool content',
            author=test_user_1,
            image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
            times_read=45
        )

        Subscription.objects.create(subscriber=test_user_2,
                                    subscribe_to=test_user_1)

    def test_correct_response_for_nonexistent_article(self):
        response = self.client.post(reverse('public:subscription-through-detail',
                                            kwargs={'pk': 878}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_not_logged_user(self):
        article = Article.objects.get(title='Title')
        response = self.client.post(reverse('public:subscription-through-detail',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot subscribe to this author while you are not authenticated')

    def test_correct_response_for_logged_user_that_is_subscribed_to_author(self):
        article = Article.objects.get(title='Title')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-detail',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully unsubscribed from this author')
        subscription_object = Subscription.objects.filter(
            Q(subscribe_to=article.author) &
            Q(subscriber__username='User2')
        ).first()
        self.assertTrue(subscription_object is None)

    def test_correct_response_for_logged_user_that_is_not_subscribed_to_author(self):
        article = Article.objects.get(title='Title')
        login = self.client.login(
            username='User3', password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-detail',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully subscribed to this author')
        subscription_object = Subscription.objects.filter(
            Q(subscribe_to=article.author) &
            Q(subscriber__username='User3')
        ).first()
        self.assertTrue(subscription_object is not None)

    def test_correct_response_when_author_to_subscribe_to_and_logged_user_are_the_same_person(self):
        article = Article.objects.get(title='Title')
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-detail',
                                            kwargs={'pk': article.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:article-detail',
                                               kwargs={'pk': article.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot subscribe to yourself')


class ArticlesByTagViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('public:articles-tag',
                                           kwargs={'slug': 'some_tag'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/articles_by_tag.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('public:articles-tag',
                                           kwargs={'slug': 'some_tag'}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.context)
        self.assertTrue('tag' in response.context)


class SearchArticlesViewTest(TestCase):

    def test_correct_response_to_empty_search(self):
        response = self.client.get(reverse('public:search') + '?query=')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/empty_search.html')

    def test_correct_response_when_search_query_consists_only_from_hashtag(self):
        response = self.client.get(reverse('public:search') + '?query=#')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/empty_search.html')

    def test_view_uses_correct_template(self):
        query = 'something'
        response = self.client.get(
            reverse('public:search') + f'?query={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/search_results.html')

    def test_correct_objects_in_context(self):
        query = 'something'
        response = self.client.get(
            reverse('public:search') + f'?query={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.context)
        self.assertTrue('query' in response.context)

    def test_redirect_when_searching_for_tag(self):
        tag = 'tag'
        response = self.client.get(
            reverse('public:search') + f'?query=%{tag}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:articles-tag',
                                               kwargs={'slug': tag}))


class AuthorPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')
        test_user_4 = CustomUser.objects.create_user(username='User4',
                                                     password='34somepassword34',
                                                     email='user4@gmail.com')

        Subscription.objects.create(subscriber=test_user_2,
                                    subscribe_to=test_user_1)

        Subscription.objects.create(subscriber=test_user_3,
                                    subscribe_to=test_user_1)

    def test_correct_response_to_nonexistent_author(self):
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': 876}))
        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/author_page.html')

    def test_correct_objects_in_context(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('subscribers' in response.context)
        self.assertTrue('author' in response.context)
        self.assertTrue('subscription_status' in response.context)

    def test_correct_subscription_status_for_logged_user_that_is_subscribed_to_author(self):
        author = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['subscription_status'], 'Unsubscribe')

    def test_correct_subscription_status_for_logged_user_that_is_not_subscribed_to_author(self):
        author = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User4',
                                  password='34somepassword34')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['subscription_status'], 'Subscribe')

    def test_correct_subscription_status_for_not_logged_user(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['subscription_status'], 'Subscribe')

    def test_view_calculates_number_of_subscribers_correctly(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:author-page',
                                           kwargs={'pk': author.id}))
        number_of_author_subscribers = Subscription.objects.\
            filter(subscribe_to=author).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subscribers'],
                         number_of_author_subscribers)


class SubscribeUnsubscribeThroughAuthorPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        test_user_3 = CustomUser.objects.create_user(username='User3',
                                                     password='34somepassword34',
                                                     email='user3@gmail.com')

        Subscription.objects.create(subscriber=test_user_2,
                                    subscribe_to=test_user_1)

    def test_correct_response_for_nonexistent_author(self):
        response = self.client.post(reverse('public:subscription-through-author',
                                            kwargs={'pk': 598}))
        self.assertEqual(response.status_code, 404)

    def test_correct_response_for_not_logged_user(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.post(reverse('public:subscription-through-author',
                                            kwargs={'pk': author.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:author-page',
                                               kwargs={'pk': author.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot subscribe to this author while you are not authenticated')

    def test_correct_response_to_logged_user_that_is_subscribed_to_author(self):
        author = CustomUser.objects.get(username='User1')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-author',
                                            kwargs={'pk': author.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:author-page',
                                               kwargs={'pk': author.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully unsubscribed from this author')
        subscription_object = Subscription.objects.filter(
            Q(subscribe_to=author) &
            Q(subscriber__username='User2')
        ).first()
        self.assertTrue(subscription_object is None)

    def test_correct_response_to_logged_user_that_is_not_subscribed_to_author(self):
        author = CustomUser.objects.get(username='User1')
        login = self.client.login(
            username='User3', password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-author',
                                            kwargs={'pk': author.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:author-page',
                                               kwargs={'pk': author.id}))
        self.assertEqual(str(messages[0]),
                         'You successfully subscribed to this author')
        subscription_object = Subscription.objects.filter(
            Q(subscribe_to=author) &
            Q(subscriber__username='User3')
        ).first()
        self.assertTrue(subscription_object is not None)

    def test_correct_response_when_author_to_subscribe_to_and_logged_user_are_the_same_person(self):
        author = CustomUser.objects.get(username='User1')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('public:subscription-through-author',
                                            kwargs={'pk': author.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public:author-page',
                                               kwargs={'pk': author.id}))
        self.assertEqual(str(messages[0]),
                         'You cannot subscribe to yourself')


class ArticlesByAuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CustomUser.objects.create_user(username='User1',
                                       password='34somepassword34')

    def test_correct_response_to_nonexistent_author(self):
        response = self.client.get(reverse('public:articles-by-author',
                                           kwargs={'pk': 990}))
        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:articles-by-author',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/articles_by_author.html')

    def test_correct_objects_in_context(self):
        author = CustomUser.objects.get(username='User1')
        response = self.client.get(reverse('public:articles-by-author',
                                           kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('author' in response.context)
        self.assertTrue('articles' in response.context)
