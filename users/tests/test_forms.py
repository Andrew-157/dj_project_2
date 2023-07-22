from django.test import TestCase

from users.forms import UserCreationForm, UserChangeForm


class UserCreationFormTest(TestCase):

    def test_email_help_text(self):
        form = UserCreationForm()
        help_text = form.fields['email'].help_text
        self.assertEqual(help_text, 'Required. Enter a valid email address.')

    def test_user_image_help_test(self):
        form = UserCreationForm()
        help_text = form.fields['user_image'].help_text
        self.assertEqual(help_text, 'You can register without an image.')


class UserChangeFormTest(TestCase):

    def test_email_help_text(self):
        form = UserChangeForm()
        help_text = form.fields['email'].help_text
        self.assertEqual(help_text, 'Required. Enter a valid email address.')
