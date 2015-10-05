from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Video(models.Model):
    video_file = models.FileField(upload_to='video')
    preview_file = models.ImageField(upload_to='preview', null=True, blank=True)

    length = models.IntegerField()  # length of video in seconds
    add_time = models.DateTimeField(auto_now_add=True)
    nsfw_source = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)

    nsfw = models.ManyToManyField(User, through='UserNsfw', related_name='video_nsfw')
    favourite = models.ManyToManyField(User, through='UserFavourite', related_name='video_favourite')
    like = models.ManyToManyField(User, through='UserLike', related_name='video_like')

    tag = models.ManyToManyField(Tag, through='TagVideo')  # global tags, not user-specific


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


class TagVideo(models.Model):
    tag = models.ForeignKey(Tag)
    video = models.ForeignKey(Video)
    hard = models.BooleanField(default=False)  # True for tags not derived from UserTag

    class Meta:
        unique_together = ('tag', 'video')


class UserTagVideo(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    video = models.ForeignKey(Video)

    class Meta:
        unique_together = ('user', 'tag', 'video')
