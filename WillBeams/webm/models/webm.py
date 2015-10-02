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

    def _change_rating(self, value):
        self.rating = F('rating') + value
        self.save()

    def increase_rating(self):
        self._change_rating(1)

    def decrease_rating(self):
        self._change_rating(-1)

    @classmethod
    def get_or_increase_rating(cls, md5):
        webm, created = cls.objects.get_or_create(md5=md5)

        if not created:
            webm.increase_rating()

        return webm, created

    def __str__(self):
        return self.thumbnail.url.split('/')[-1]

    class Meta:
        ordering = ['-rating']
