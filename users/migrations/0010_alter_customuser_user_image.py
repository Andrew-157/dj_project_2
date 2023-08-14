# Generated by Django 4.2.3 on 2023-08-14 10:42

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_image',
            field=models.ImageField(null=True, upload_to='users/images', validators=[users.models.validate_image]),
        ),
    ]