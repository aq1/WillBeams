import os
from django.utils import timezone

from django.db import models
from django.db.models import F

from . import Tag


def get_media_folder(instance, filename):
    today = timezone.now().strftime('%Y/%m/%d/%H/%M')
    return '/'.join((os.path.splitext(filename)[-1][1:], today))


class Webm(models.Model):
    video = models.FileField(
        upload_to=get_media_folder, blank=True, default='')
    thumbnail = models.ImageField(upload_to=get_media_folder)
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
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

    def __str__(self):
        return self.thumbnail.url.split('/')[-1]

    class Meta:
        ordering = ['-rating']

