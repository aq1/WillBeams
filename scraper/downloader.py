import os
import sys

import threading

from connection import Connection
import utils

sys.path.append(utils.DJANGO_PROJECT_DIR)
sys.path.append(utils.BASE_DIR)

import django
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError


from newapp.models import Webm, get_media_folder, WebmUrl, Tag
import scraper


os.environ["DJANGO_SETTINGS_MODULE"] = 'WillBeams.settings'
django.setup()


def save(self, filename, webm, thumb):
    if not filename:
        return

    if webm:
        filename += '.webm'
        path = os.path.join(
            get_media_folder(self._webm_obj, filename), filename)
        webm_path = default_storage.save(path, ContentFile(webm))
        self._webm_obj.video = webm_path

    if thumb:
        filename += '.jpg'
        path = os.path.join(
            get_media_folder(self._webm_obj, filename), filename)
        thumb_path = default_storage.save(path, ContentFile(thumb))
        self._webm_obj.thumbnail = thumb_path

    try:
        self._webm_obj.save()
    except IntegrityError as e:
        self._webm_obj = Webm.objects.get(md5=self._webm_obj.md5)
        scraper.inform(e, level=scraper.WARNING)
    finally:
        self._add_releated_info()


def callback(ch, method, properties, body):

    try:
        url, thumb, md5, size = body.decode('utf8').split()
    except (ValueError, UnicodeDecodeError):
        utils.inform('unexpected format: "{}"'.format(body), level=utils.ERROR)

    utils.inform(body, level=utils.IMPORTANT_INFO)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def work(channel, q_name):
    channel.basic_consume(callback,
                          queue=q_name,
                          no_ack=False)
    channel.start_consuming()


def start_thread(channel, q_name):
    threading.Thread(target=work,
                     args=[channel, q_name]).start()

    utils.inform('Download thread started', level=utils.IMPORTANT_INFO)
