from django.db import models


class Tag(models.Model):

    name = models.CharField(max_length=31, unique=True)

    def __str__(self):
        return self.name
