from django.contrib.auth.models import User, Group
from .models import Webm, Tag
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('name','webm_set')

class WebmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Webm
        fields = ('thumbnail', 'rating', 'nsfw', 'tags', 'added')

