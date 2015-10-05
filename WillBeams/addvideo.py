# usage:
# from WillBeams.addvideo import add_prepared_video
# add_prepared_video('/tmp/vid.webm', 35, preview_filename='/tmp/vid.jpg', tags=('anime', 'vg'))

import django
from django.conf import settings, Settings
from os.path import dirname, abspath
import sys
from django.apps import apps


BASE_DIR = dirname(abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

if not apps.ready:
    settings.configure(default_settings=Settings('settings'))
    django.setup()


from django.core.files import File
from newapp.models import Webm, Tag


def add_prepared_video(video_filename, video_length, preview_filename=None, nsfw_source=False, tags=None):
    webm = Webm()
    webm.video = File(open(video_filename, 'rb'))
    video.length = video_length
    if preview_filename is not None:
        webm.thumb = File(open(preview_filename, 'rb'))
    webm.nsfw_source = nsfw_source
    webm.save()

    for tname in ([] if tags is None else tags):
        tag, _ = Tag.objects.get_or_create(name=tname)
        webm.tagvideo_set.create(tag=tag, hard=True)