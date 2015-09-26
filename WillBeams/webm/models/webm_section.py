from django.db import models

from . import Webm, Section


class WebmSection(models.Model):
    webm = models.ForeignKey(Webm)
    section = models.ForeignKey(Section)
