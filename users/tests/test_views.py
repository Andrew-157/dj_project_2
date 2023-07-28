from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class RegisterUserViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_response_if_invalid_data_posted(self):
        response = self.client.post(reverse('users:register'),
                                    data={'username': 'u',
                                          'email': 'user12@gmail.com',
                                          'password1': '34password34',
                                          'password2': '34password34'})
        self.assertEqual(response.status_code, 200)

    def test_correct_response_if_successful_registration(self):
        response = self.client.post(reverse('users:register'),
                                    data={'username': 'user12',
                                          'email': 'user12@gmail.com',
                                          'password1': '34password34',
                                          'password2': '34password34'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(str(messages[0]), 'You were successfully registered')
        new_user = CustomUser.objects.filter(username='user12').filter()
        self.assertTrue(new_user is not None)


class LoginUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = CustomUser.objects.create_user(username='some_user',
                                                   password='34somepassword34',
                                                   email='someone@gmail.com')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_response_if_invalid_data_posted(self):
        response = self.client.post(reverse('users:login'),
                                    data={
                                        'username': 'someone@gmail.com',
                                        'password': 'wrongpassword123'})
        self.assertEqual(response.status_code, 200)

    def test_correct_response_if_successful_login(self):
        response = self.client.post(reverse('users:login'),
                                    data={
                                        'username': 'some_user',
                                        'password': '34somepassword34'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(str(messages[0]), 'Welcome back')
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class ChangeUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        user = CustomUser.objects.create_user(username='some_user',
                                              password='34somepassword34',
                                              email='someone@gmail.com')

    def test_correct_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('users:change-user'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_view_uses_correct_template(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.get(reverse('users:change-user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_user.html')

    def test_correct_objects_in_context(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.get(reverse('users:change-user'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_correct_response_if_invalid_data_posted(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.post(reverse('users:change-user'),
                                    data={'username': 'u',
                                          'email': 'invalid'})
        self.assertEqual(response.status_code, 200)

    def test_response_if_valid_data_posted(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.post(reverse('users:change-user'),
                                    data={'username': 'valid_name',
                                          'email': 'valid@gmail.com'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(
            str(messages[0]), 'You successfully changed your credentials')
        self.assertEqual(response.wsgi_request.user.username, 'valid_name')
