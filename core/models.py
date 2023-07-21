from django.db import models
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager


def validate_image(image):
    file_size = image.file.size
    limit_kb = 1000
    if file_size > limit_kb * 1024:
        raise ValidationError(f"Maximum size of the image is {limit_kb} KB")

    # file_size = image.file.size
    # limit_mb = 8
    # if file_size > limit_mb * 1024 * 1024:
    #     raise ValidationError(f"Maximum size of the image is {limit_mb} MB")


class Article(models.Model):
    title = models.CharField(max_length=255, null=False)
    content = models.TextField()
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='core/images', null=False, validators=[validate_image]
    )
    times_read = models.BigIntegerField(default=0)
    tags = TaggableManager(
        help_text='Use comma to separate tags, # is not needed to add tag')
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
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content


class FavoriteArticles(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    articles = models.ManyToManyField('core.Article')


class Reaction(models.Model):
    value = models.SmallIntegerField()
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    article = models.ForeignKey('core.Article', on_delete=models.CASCADE)
    reaction_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    article = models.ForeignKey('core.Article', on_delete=models.CASCADE)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class UserReading(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    article = models.ForeignKey('core.Article', on_delete=models.CASCADE)
    date_read = models.DateTimeField()


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        'users.CustomUser', related_name='subscriber', on_delete=models.CASCADE)
    subscribe_to = models.ForeignKey(
        'users.CustomUser', related_name='subscribe_to', on_delete=models.CASCADE)
