# Generated by Django 4.2 on 2023-05-23 11:25

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ImageField(upload_to='core/images', validators=[core.models.validate_image]),
        ),
    ]
