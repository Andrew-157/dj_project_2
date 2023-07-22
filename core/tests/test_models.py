from django.test import TestCase

from core.models import Subscription
from users.models import CustomUser


class SubscriptionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        Subscription.objects.create(subscriber=test_user_2,
                                    subscribe_to=test_user_1)

    def test_subscribe_to_label(self):
        sub_obj = Subscription.objects.get(subscribe_to__username='User1')
        field_label = sub_obj._meta.get_field('subscribe_to').verbose_name
        self.assertEqual(field_label, 'subscribe to')

    def test_subscriber_label(self):
        sub_obj = Subscription.objects.get(subscribe_to__username='User1')
        field_label = sub_obj._meta.get_field('subscriber').verbose_name
        self.assertEqual(field_label, 'subscriber')
