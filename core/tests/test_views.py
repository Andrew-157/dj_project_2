from django.test import TestCase
from django.urls import reverse


class BecomeUserViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('core:become-user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/become_user.html')
