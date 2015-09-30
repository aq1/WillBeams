# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webmsection',
            name='section',
        ),
        migrations.RemoveField(
            model_name='webmsection',
            name='webm',
        ),
        migrations.RemoveField(
            model_name='webmtag',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='webmtag',
            name='webm',
        ),
        migrations.AddField(
            model_name='webm',
            name='tags',
            field=models.ManyToManyField(to='webm.Tag'),
        ),
        migrations.DeleteModel(
            name='Section',
        ),
        migrations.DeleteModel(
            name='WebmSection',
        ),
        migrations.DeleteModel(
            name='WebmTag',
        ),
    ]
