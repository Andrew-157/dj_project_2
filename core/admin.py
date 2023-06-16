from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from django.db.models.query_utils import Q
from users.models import CustomUser
from core.models import Article, Comment, Reaction


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'times_read',
                    'pub_date', 'tag_list', 'image_tag',
                    'comments', 'likes', 'dislikes']
    list_filter = ['title', 'tags', 'author', 'pub_date']
    search_fields = ['title']

    def get_queryset(self, request):
        return super().get_queryset(request).\
            select_related('author').\
            prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def image_tag(self, obj):
        return format_html(f'<img src="{obj.image.url}" width="50" height="50">')

    image_tag.short_description = 'Article image'

    def comments(self, obj):
        return Comment.objects.filter(article__id=obj.id).count()

    def likes(self, obj):
        return Reaction.objects.filter(
            Q(article__id=obj.id) &
            Q(value=1)
        ).count()

    def dislikes(self, obj):
        return Reaction.objects.filter(
            Q(article__id=obj.id) &
            Q(value=-1)
        ).count()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'date_joined',
        'is_superuser', 'is_active', 'is_staff',
        'image_tag'
    ]
    list_filter = ['username', 'date_joined']
    search_fields = ['username']
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.is_superuser:
            return None
        return format_html(f'<img src="{obj.user_image.url}" width="100" height="100">')
    image_tag.short_description = "User's image"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'article', 'pub_date'
    ]
    list_filter = ['user', 'article', 'pub_date']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).\
            select_related('user').\
            select_related('article')
