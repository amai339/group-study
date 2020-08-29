# Generated by Django 2.1.7 on 2019-05-07 07:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('room', '0004_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='admin',
            field=models.ManyToManyField(related_name='admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='invited',
            field=models.ManyToManyField(related_name='invited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FilePathField(path='C:\\Users\\sadox\\PycharmProjects\\GroupStudyApp\\media'),
        ),
    ]
