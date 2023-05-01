from django import forms
from core.models import Article


class PublishUpdateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = [
            'author', 'times_read', 'pub_date'
        ]
