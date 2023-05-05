from django import forms
from core.models import Comment


class CommentArticleForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
