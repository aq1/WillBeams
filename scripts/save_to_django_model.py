import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'WillBeams'))
sys.path.append(BASE_DIR)


import django
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError


os.environ["DJANGO_SETTINGS_MODULE"] = 'WillBeams.settings'
django.setup()

from webm.models import Webm, get_media_folder, WebmUrl, Tag
import scraper


def _except_unique_violation(function):

    def _f(self):
        try:
            return function(self)
        except IntegrityError as e:
            scraper.inform(e, level=scraper.WARNING)
    return _f


class DownloadToModel(scraper.Downloader):

    def __init__(self, *args, **kwargs):
        self._webm_obj = None
        self._webm_url = None
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_section(webm_url):
        splitted = webm_url.split('/')
        return splitted[0] or splitted[1] or None

    @_except_unique_violation
    def _add_webm_url(self):
        WebmUrl.objects.create(webm=self._webm_obj, url=self._webm_url)

    @_except_unique_violation
    def _add_webm_section_tag(self):
        tag, _ = Tag.objects.get_or_create(
            name=self._get_section(self._webm_url))
        self._webm_obj.tags.add(tag)

    def _add_releated_info(self):
        self._add_webm_url()
        self._add_webm_section_tag()

    def _download(self, data):
        self._webm_url, md5 = data[0], data[-1]
        self._webm_obj, created = Webm.get_or_increase_rating(md5)

        if not created:
            result = None, None, None
            scraper.inform(
                'Increase rating {}'.format(self._webm_url), level=scraper.WARNING)
            self._add_releated_info()
        else:
            result = super()._download(data)

        return result

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

    def work(self, *args, **kwargs):
        return super().work(self.save)


if __name__ == '__main__':
    sections = ['vg', 'b', 'a', 'mov']
    worker = scraper.MainWorker(sections, downloader=DownloadToModel)
    worker.work()
