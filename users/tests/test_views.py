from django.contrib import auth
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from users.forms import UserCreationForm, UserChangeForm


class RegisterUserViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], UserCreationForm))

    def test_correct_response_if_invalid_data_posted(self):
        response = self.client.post(reverse('users:register'),
                                    data={'username': 'u',
                                          'email': 'user12@gmail.com',
                                          'password1': '34password34',
                                          'password2': '34password34'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        error_message = b'Username cannot be shorter than 6 characters.'
        self.assertTrue(error_message in response.content)

    def test_correct_response_if_empty_data_posted(self):
        response = self.client.post(reverse('users:register'),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        error_message = 'This field is required.'
        self.assertTrue(error_message.encode() in response.content)
        decoded_content: str = response.content.decode()
        self.assertEqual(decoded_content.count(error_message), 4)

    def test_correct_response_if_no_data_posted(self):
        response = self.client.post(reverse('users:register'),
                                    data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        error_message = 'This field is required.'
        self.assertTrue(error_message.encode() in response.content)
        decoded_content: str = response.content.decode()
        self.assertEqual(decoded_content.count(error_message), 4)

    def test_register_with_duplicate_username(self):
        existing_username = 'test_user'
        CustomUser.objects.create_user(username=existing_username,
                                       email='test_user@gmail.com',
                                       password='34somepassword34')
        response = self.client.post(reverse('users:register'),
                                    data={'username': existing_username,
                                          'email': 'new_user@gmail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        error_message = b'A user with that username already exists.'
        self.assertTrue(error_message in response.content)

    def test_register_with_duplicate_email(self):
        existing_email = 'test_user@gmail.com'
        CustomUser.objects.create_user(username='test_user',
                                       email=existing_email,
                                       password='34somepassword34')
        response = self.client.post(reverse('users:register'),
                                    data={'username': 'new_user',
                                          'email': existing_email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        error_message = b'User with this Email already exists.'
        self.assertTrue(error_message in response.content)

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
        new_user = CustomUser.objects.filter(username='user12').first()
        self.assertTrue(new_user is not None)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(new_user, user)


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
        self.assertTemplateUsed(response, 'users/login.html')

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


class LogoutViewTest(TestCase):

    def test_correct_response_to_not_logged_user(self):
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'You have successfully logged out.')

    def test_correct_response_to_logged_user(self):
        username = 'new_user'
        password = '34somepassword34'
        CustomUser.objects.create_user(
            username=username,
            email='new_user@gmail.com',
            password=password
        )
        login = self.client.login(username=username,
                                  password=password)
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'You have successfully logged out.')
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


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
        response = self.client.post(reverse('users:change-user'))
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
        self.assertTrue(isinstance(response.context['form'], UserChangeForm))

    def test_correct_response_if_invalid_data_posted(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.post(reverse('users:change-user'),
                                    data={'username': 'u',
                                          'email': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_user.html')
        error_message = b'Username cannot be shorter than 6 characters.'
        self.assertTrue(error_message in response.content)

    def test_correct_response_if_empty_data_posted(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.post(reverse('users:change-user'),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_user.html')
        error_message = 'This field is required'
        self.assertTrue(error_message.encode() in response.content)
        decoded_content: str = response.content.decode()
        self.assertEqual(decoded_content.count(error_message), 2)

    def test_correct_response_if_no_data_posted(self):
        login = self.client.login(username='some_user',
                                  password='34somepassword34')
        response = self.client.post(reverse('users:change-user'),
                                    data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_user.html')
        error_message = 'This field is required'
        self.assertTrue(error_message.encode() in response.content)
        decoded_content: str = response.content.decode()
        self.assertEqual(decoded_content.count(error_message), 2)

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
