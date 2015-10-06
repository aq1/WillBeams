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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TagWebm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hard', models.BooleanField(default=False)),
                ('tag', models.ForeignKey(to='newapp.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='UserFavourite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserNsfw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='UserTagWebm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('tag', models.ForeignKey(to='newapp.Tag')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('active_time', models.IntegerField()),
                ('passive_time', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, default=None, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Webm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('video', models.FileField(upload_to='video')),
                ('thumb', models.ImageField(upload_to='preview', blank=True, null=True)),
                ('length', models.IntegerField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('nsfw_source', models.BooleanField(default=False)),
                ('blacklisted', models.BooleanField(default=False)),
                ('favourite', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='webm_favourite', through='newapp.UserFavourite')),
                ('likes', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='webm_like', through='newapp.UserLike')),
                ('nsfw', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='webm_nsfw', through='newapp.UserNsfw')),
                ('tag', models.ManyToManyField(to='newapp.Tag', through='newapp.TagWebm')),
            ],
        ),
        migrations.AddField(
            model_name='view',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm'),
        ),
        migrations.AddField(
            model_name='usertagwebm',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm'),
        ),
        migrations.AddField(
            model_name='usernsfw',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+'),
        ),
        migrations.AddField(
            model_name='userlike',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+'),
        ),
        migrations.AddField(
            model_name='userfavourite',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+'),
        ),
        migrations.AddField(
            model_name='tagwebm',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm'),
        ),
        migrations.AlterUniqueTogether(
            name='usertagwebm',
            unique_together=set([('user', 'tag', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='usernsfw',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='userlike',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='userfavourite',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='tagwebm',
            unique_together=set([('tag', 'webm')]),
        ),
    ]
