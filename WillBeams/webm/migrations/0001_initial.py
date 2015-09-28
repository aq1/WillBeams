# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import webm.models.webm


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=31)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=31)),
            ],
        ),
        migrations.CreateModel(
            name='Webm',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to=webm.models.webm.get_media_folder, default='', blank=True)),
                ('thumbnail', models.ImageField(upload_to=webm.models.webm.get_media_folder)),
                ('rating', models.IntegerField(default=0)),
                ('md5', models.CharField(unique=True, editable=False, max_length=32)),
                ('nsfw', models.BooleanField(default=False)),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebmSection',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(to='webm.Section')),
                ('webm', models.ForeignKey(to='webm.Webm')),
            ],
        ),
        migrations.CreateModel(
            name='WebmTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('tag', models.ForeignKey(to='webm.Tag')),
                ('webm', models.ForeignKey(to='webm.Webm')),
            ],
        ),
        migrations.CreateModel(
            name='WebmUrl',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2047)),
                ('webm', models.ForeignKey(to='webm.Webm')),
            ],
        ),
    ]
