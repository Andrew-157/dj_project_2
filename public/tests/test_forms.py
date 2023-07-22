from django.test import TestCase

from public.forms import CommentArticleForm


class CommentArticleFormTest(TestCase):

    def test_content_label(self):
        form = CommentArticleForm()
        field_label = form.fields['content'].label
        self.assertEqual(field_label, 'Content')
