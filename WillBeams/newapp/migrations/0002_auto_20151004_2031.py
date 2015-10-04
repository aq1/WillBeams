# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hard', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='tag',
            name='video',
        ),
        migrations.AddField(
            model_name='tagvideo',
            name='tag',
            field=models.ForeignKey(to='newapp.Tag'),
        ),
        migrations.AddField(
            model_name='tagvideo',
            name='video',
            field=models.ForeignKey(to='newapp.Video'),
        ),
        migrations.AddField(
            model_name='video',
            name='tag',
            field=models.ManyToManyField(to='newapp.Tag', through='newapp.TagVideo'),
        ),
        migrations.AlterUniqueTogether(
            name='tagvideo',
            unique_together=set([('tag', 'video')]),
        ),
    ]
