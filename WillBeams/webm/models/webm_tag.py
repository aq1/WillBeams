from django.db import models

from . import Webm, Tag


class WebmTag(models.Model):
    webm = models.ForeignKey(Webm)
    tag = models.ForeignKey(Tag)

    class Meta:
        unique_together = [('webm', 'tag')]

    def __str__(self):
        return '{}: {}'.format(self.tag, self.webm)
