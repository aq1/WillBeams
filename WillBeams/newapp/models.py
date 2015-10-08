from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Webm(models.Model):
    video = models.FileField(upload_to='video')
    thumb = models.ImageField(upload_to='preview', null=True, blank=True)

    length = models.IntegerField()  # length of video in seconds
    added = models.DateTimeField(auto_now_add=True)
    nsfw_source = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)

    nsfw = models.ManyToManyField(
        User, through='UserNsfw', related_name='webm_nsfw')
    favourite = models.ManyToManyField(
        User, through='UserFavourite', related_name='webm_favourite')
    likes = models.ManyToManyField(
        User, through='UserLike', related_name='webm_like')

    # global tags, not user-specific
    tag = models.ManyToManyField(Tag, through='TagWebm')

    def __str__(self):
        return self.thumb.url.split('/')[-1] if self.thumb else 'No thumbnail'

    class Meta:
        ordering = ['-added']


class View(models.Model):
    # nullable for anonymous viewers
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    # TODO: test uniqueness allows duplication on NULL
    webm = models.ForeignKey(Webm)

    # time when user started to watch
    start_time = models.DateTimeField(auto_now_add=True)
    # number of seconds user actively watched
    active_time = models.IntegerField()
    # number of seconds video played but user didn't watch it
    passive_time = models.IntegerField()


class UserNsfw(models.Model):
    user = models.ForeignKey(User, related_name='+')
    webm = models.ForeignKey(Webm, related_name='+')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'webm')


class UserFavourite(models.Model):
    user = models.ForeignKey(User, related_name='+')
    webm = models.ForeignKey(Webm, related_name='userfavourite')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'webm')


class UserLike(models.Model):
    user = models.ForeignKey(User, related_name='+')
    webm = models.ForeignKey(Webm, related_name='userlike')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'webm')


class TagWebm(models.Model):
    tag = models.ForeignKey(Tag)
    webm = models.ForeignKey(Webm)
    # True for tags not derived from UserTag
    hard = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tag', 'webm')


class UserTagWebm(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    webm = models.ForeignKey(Webm)

    class Meta:
        unique_together = ('user', 'tag', 'webm')
