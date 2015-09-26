from django.db import models

from . import Webm, Tag


class WebmTag(models.Model):
    webm = models.ForeignKey(Webm)
    tag = models.ForeignKey(Tag)
