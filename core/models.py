from django.db import models
from taggit.managers import TaggableManager


class Article(models.Model):
    title = models.CharField(max_length=255, null=False)
    content = models.TextField()
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='core/images', null=False
    )
    times_read = models.BigIntegerField(default=0)
    tags = TaggableManager(help_text='Use comma to separate tags')
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SocialMedia(models.Model):
    FACEBOOK = 'FB'
    INSTAGRAM = 'IM'
    YOUTUBE = 'YB'
    TIKTOK = 'TT'
    TWITTER = 'TW'
    SOCIAL_MEDIA_TITLES = [
        (FACEBOOK, 'Facebook'),
        (INSTAGRAM, 'Instagram'),
        (YOUTUBE, 'Youtube'),
        (TIKTOK, 'TikTok'),
        (TWITTER, 'Twitter')
    ]
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    link = models.URLField(max_length=128, unique=True)
    title = models.CharField(max_length=2, choices=SOCIAL_MEDIA_TITLES)


class UserDescription(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content


class PersonalArticlesCollection(models.Model):
    title = models.CharField(max_length=155)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    articles = models.ManyToManyField('core.Article')


class PublicArticlesCollection(models.Model):
    title = models.CharField(max_length=155)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    articles = models.ManyToManyField('core.Article')
