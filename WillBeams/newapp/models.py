from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    url = models.SlugField(unique=True)
    length = models.IntegerField()  # length of video in seconds
    add_time = models.DateTimeField(auto_now_add=True)
    nsfw_source = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)

    nsfw = models.ManyToManyField(User, through='UserNsfw', related_name='video_nsfw')
    favourite = models.ManyToManyField(User, through='UserFavourite', related_name='video_favourite')
    like = models.ManyToManyField(User, through='UserLike', related_name='video_like')


class View(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, default=None)  # nullable for anonymous viewers
    # TODO: test uniqueness allows duplication on NULL
    video = models.ForeignKey(Video)

    start_time = models.DateTimeField(auto_now_add=True)  # time when user started to watch
    active_time = models.IntegerField()  # number of seconds user actively watched
    passive_time = models.IntegerField()  # number of seconds video played but user didn't watch it


class UserNsfw(models.Model):
    user = models.ForeignKey(User, related_name='+')
    video = models.ForeignKey(Video, related_name='+')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')


class UserFavourite(models.Model):
    user = models.ForeignKey(User, related_name='+')
    video = models.ForeignKey(Video, related_name='+')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')


class UserLike(models.Model):
    user = models.ForeignKey(User, related_name='+')
    video = models.ForeignKey(Video, related_name='+')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    video = models.ManyToManyField(Video)  # global tags for everyone


class UserTagVideo(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    video = models.ForeignKey(Video)

    class Meta:
        unique_together = ('user', 'tag', 'video')
