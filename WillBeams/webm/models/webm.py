import os
from datetime import datetime

from django.db import models
from django.db.models import F


def get_media_folder(instance, filename):
    today = datetime.now().strftime('%Y/%m/%d/%H/%M')
    return '/'.join((os.path.splitext(filename)[-1][1:], today))


class Webm(models.Model):
    video = models.FileField(
        upload_to=get_media_folder, blank=True, default='')
    thumbnail = models.ImageField(upload_to=get_media_folder)
    rating = models.IntegerField(default=0)
    md5 = models.CharField(unique=True, max_length=32,
                           editable=False)
    nsfw = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)

    @classmethod
    def _change_rating(cls, md5, value):
        webm = cls.objects.get(md5=md5)
        webm.rating = F('rating') + value
        webm.save()
        return webm

    @classmethod
    def increase_rating(cls, md5):
        return cls._change_rating(md5, 1)

    @classmethod
    def decrease_rating(cls, md5):
        return cls._change_rating(md5, -1)

    def is_safe_for_work(self):
        return not self.nsfw

    is_safe_for_work.boolean = True
    is_safe_for_work.short_description = 'Safe for work?'

    def thumbnail_img(self):
        html = '<img style="max-width:100%%; \
                max-height:100%%; width:200px;" \
                src="%s" alt="No thumb">'
        try:
            return html % self.thumbnail.url
        except ValueError:
            return html % ''

    thumbnail_img.allow_tags = True

    def __unicode__(self):
        try:
            return self.thumbnail.url.split('/')[-1]
        except ValueError:
            return self.md5
