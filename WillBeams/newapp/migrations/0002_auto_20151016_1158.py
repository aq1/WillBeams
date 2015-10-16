# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='webm',
            options={'ordering': ['-added']},
        ),
        migrations.AddField(
            model_name='webm',
            name='height',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webm',
            name='thumb_a1',
            field=models.ImageField(blank=True, null=True, upload_to='thumba1'),
        ),
        migrations.AddField(
            model_name='webm',
            name='thumb_a2',
            field=models.ImageField(blank=True, null=True, upload_to='thumba2'),
        ),
        migrations.AddField(
            model_name='webm',
            name='thumb_b1',
            field=models.ImageField(blank=True, null=True, upload_to='thumbb1'),
        ),
        migrations.AddField(
            model_name='webm',
            name='thumb_b2',
            field=models.ImageField(blank=True, null=True, upload_to='thumbb2'),
        ),
        migrations.AddField(
            model_name='webm',
            name='width',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userfavourite',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='userfavourite'),
        ),
        migrations.AlterField(
            model_name='userlike',
            name='webm',
            field=models.ForeignKey(to='newapp.Webm', related_name='userlike'),
        ),
        migrations.AlterField(
            model_name='webm',
            name='thumb',
            field=models.ImageField(blank=True, null=True, upload_to='thumb'),
        ),
    ]
