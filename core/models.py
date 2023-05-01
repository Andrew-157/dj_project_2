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
