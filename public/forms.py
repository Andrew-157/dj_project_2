from django import forms
from core.models import Comment


class PublishComment(forms.ModelForm):

    class Meta:
        model = Comment
        fields = [
            'content'
        ]
