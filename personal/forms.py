from django import forms
from core.models import Article, Comment, SocialMedia


class PublishArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'pub_date', 'times_read']


class SocialMediaForm(forms.ModelForm):

    class Meta:
        model = SocialMedia
        exclude = ['user']
