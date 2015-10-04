# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0002_auto_20151004_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='url',
        ),
        migrations.AddField(
            model_name='video',
            name='preview_file',
            field=models.ImageField(upload_to='', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='video',
            name='video_file',
            field=models.FileField(upload_to='', default=None),
            preserve_default=False,
        ),
    ]
