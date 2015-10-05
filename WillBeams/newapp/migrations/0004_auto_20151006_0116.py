# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newapp', '0003_auto_20151004_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagWebm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hard', models.BooleanField(default=False)),
                ('tag', models.ForeignKey(to='newapp.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Webm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('video', models.FileField(upload_to='video')),
                ('thumb', models.ImageField(upload_to='preview', null=True, blank=True)),
                ('length', models.IntegerField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('nsfw_source', models.BooleanField(default=False)),
                ('blacklisted', models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameModel(
            old_name='UserTagVideo',
            new_name='UserTagWebm',
        ),
        migrations.AlterUniqueTogether(
            name='tagvideo',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='tagvideo',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='tagvideo',
            name='video',
        ),
        migrations.RemoveField(
            model_name='video',
            name='favourite',
        ),
        migrations.RemoveField(
            model_name='video',
            name='like',
        ),
        migrations.RemoveField(
            model_name='video',
            name='nsfw',
        ),
        migrations.RemoveField(
            model_name='video',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='view',
            name='video',
        ),
        migrations.AlterUniqueTogether(
            name='userfavourite',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='userlike',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='usernsfw',
            unique_together=set([('user', 'webm')]),
        ),
        migrations.AlterUniqueTogether(
            name='usertagwebm',
            unique_together=set([('user', 'tag', 'webm')]),
        ),
        migrations.DeleteModel(
            name='TagVideo',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
        migrations.AddField(
            model_name='webm',
            name='favourite',
            field=models.ManyToManyField(related_name='webm_favourite', to=settings.AUTH_USER_MODEL, through='newapp.UserFavourite'),
        ),
        migrations.AddField(
            model_name='webm',
            name='likes',
            field=models.ManyToManyField(related_name='webm_like', to=settings.AUTH_USER_MODEL, through='newapp.UserLike'),
        ),
        migrations.AddField(
            model_name='webm',
            name='nsfw',
            field=models.ManyToManyField(related_name='webm_nsfw', to=settings.AUTH_USER_MODEL, through='newapp.UserNsfw'),
        ),
        migrations.AddField(
            model_name='webm',
            name='tag',
            field=models.ManyToManyField(through='newapp.TagWebm', to='newapp.Tag'),
        ),
        migrations.AddField(
            model_name='tagwebm',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm'),
        ),
        migrations.RemoveField(
            model_name='userfavourite',
            name='video',
        ),
        migrations.RemoveField(
            model_name='userlike',
            name='video',
        ),
        migrations.RemoveField(
            model_name='usernsfw',
            name='video',
        ),
        migrations.RemoveField(
            model_name='usertagwebm',
            name='video',
        ),
        migrations.AddField(
            model_name='userfavourite',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userlike',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usernsfw',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='+', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertagwebm',
            name='webm',
            field=models.ForeignKey(default=1, to='newapp.Webm'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='view',
            name='webm',
            field=models.ForeignKey(default=1, to='newapp.Webm'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='tagwebm',
            unique_together=set([('tag', 'webm')]),
        ),
    ]
