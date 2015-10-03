# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserFavourite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserNsfw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserTagVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('tag', models.ForeignKey(to='newapp.Tag')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('url', models.SlugField(unique=True)),
                ('length', models.IntegerField()),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('nsfw_source', models.BooleanField(default=False)),
                ('blacklisted', models.BooleanField(default=False)),
                ('favourite', models.ManyToManyField(through='newapp.UserFavourite', to=settings.AUTH_USER_MODEL, related_name='video_favourite')),
                ('like', models.ManyToManyField(through='newapp.UserLike', to=settings.AUTH_USER_MODEL, related_name='video_like')),
                ('nsfw', models.ManyToManyField(through='newapp.UserNsfw', to=settings.AUTH_USER_MODEL, related_name='video_nsfw')),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('active_time', models.IntegerField()),
                ('passive_time', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, default=None, blank=True)),
                ('video', models.ForeignKey(to='newapp.Video')),
            ],
        ),
        migrations.AddField(
            model_name='usertagvideo',
            name='video',
            field=models.ForeignKey(to='newapp.Video'),
        ),
        migrations.AddField(
            model_name='usernsfw',
            name='video',
            field=models.ForeignKey(to='newapp.Video', related_name='+'),
        ),
        migrations.AddField(
            model_name='userlike',
            name='video',
            field=models.ForeignKey(to='newapp.Video', related_name='+'),
        ),
        migrations.AddField(
            model_name='userfavourite',
            name='video',
            field=models.ForeignKey(to='newapp.Video', related_name='+'),
        ),
        migrations.AddField(
            model_name='tag',
            name='video',
            field=models.ManyToManyField(to='newapp.Video'),
        ),
        migrations.AlterUniqueTogether(
            name='usertagvideo',
            unique_together=set([('user', 'tag', 'video')]),
        ),
        migrations.AlterUniqueTogether(
            name='usernsfw',
            unique_together=set([('user', 'video')]),
        ),
        migrations.AlterUniqueTogether(
            name='userlike',
            unique_together=set([('user', 'video')]),
        ),
        migrations.AlterUniqueTogether(
            name='userfavourite',
            unique_together=set([('user', 'video')]),
        ),
    ]
