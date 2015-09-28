from django.db import models

from . import Webm


class WebmUrl(models.Model):

    webm = models.ForeignKey(Webm)
    url = models.CharField(max_length=2047)
