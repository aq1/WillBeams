from django.db import models


class Tag(models.Model):

    name = models.CharField(max_length=31, unique=True)
    # rating = models.IntegerField()

    def __str__(self):
        return self.name

    @classmethod
    def get_top_tags(cls, count=10):
        return cls.objects.annotate(count=models.Count('webm')).order_by('-count')[:count]
