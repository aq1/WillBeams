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


def add_prepared_video(ffinfo, thumbs=[], nsfw_source=False, tags=None):
    webm = Webm()
    webm.video = File(open(ffinfo.path, 'rb'))
    webm.length = round(ffinfo.duration)
    webm.width = ffinfo.width
    webm.height = ffinfo.height

    ti_valid = lambda ti: ti >= 0 and ti < len(thumbs)
    mti = len(thumbs) // 2

    if ti_valid(mti):
        webm.thumb = File(open(thumbs[mti], 'rb'))
    if ti_valid(mti + 1):
        webm.thumb_a1 = File(open(thumbs[mti + 1], 'rb'))
    if ti_valid(mti + 2):
        webm.thumb_a2 = File(open(thumbs[mti + 2], 'rb'))
    if ti_valid(mti - 1):
        webm.thumb_b1 = File(open(thumbs[mti - 1], 'rb'))
    if ti_valid(mti - 2):
        webm.thumb_b2 = File(open(thumbs[mti - 2], 'rb'))

    webm.nsfw_source = nsfw_source
    webm.save()

    for tname in ([] if tags is None else tags):
        tag, _ = Tag.objects.get_or_create(name=tname)
        webm.tagwebm_set.create(tag=tag, hard=True)
