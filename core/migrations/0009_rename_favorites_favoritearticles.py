# Generated by Django 4.2 on 2023-05-03 12:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0008_favorites'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Favorites',
            new_name='FavoriteArticles',
        ),
    ]
