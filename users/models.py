from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


def validate_image(image):
    file_size = image.file.size
    limit_kb = 500
    if file_size > limit_kb * 1024:
        raise ValidationError(f"Maximum size of the image is {limit_kb} KB")

    # file_size = image.file.size
    # limit_mb = 8
    # if file_size > limit_mb * 1024 * 1024:
    #     raise ValidationError(f"Maximum size of the image is {limit_mb} MB")


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    user_image = models.ImageField(null=True, blank=True,
                                   upload_to='users/images', validators=[validate_image])
