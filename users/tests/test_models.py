from django.test import TestCase

from users.models import CustomUser


class CustomUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CustomUser.objects.create_user(username='User1',
                                       password='34somepassword34',
                                       email='user1@gmail.com')

    def test_user_image_label(self):
        user_obj = CustomUser.objects.get(username='User1')
        field_label = user_obj._meta.get_field('user_image').verbose_name
        self.assertEqual(field_label, 'user image')
