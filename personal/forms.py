from django import forms
from core.models import Article, SocialMedia, UserDescription, PersonalArticlesCollection


class PublishUpdateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = [
            'author', 'times_read', 'pub_date'
        ]


class PublishSocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        exclude = ['user']


class PublishUpdateUserDescriptionForm(forms.ModelForm):
    class Meta:
        model = UserDescription
        fields = ['content']
