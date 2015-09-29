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

from webm.models import Webm, get_media_folder, WebmUrl
import scraper


class DownloadToModel(scraper.Downloader):

    def __init__(self, *args, **kwargs):
        self._webm_obj = None
        self._webm_url = None
        super().__init__(*args, **kwargs)

    def _add_webm_url(self):
        WebmUrl.objects.create(webm=self._webm_obj, url=self._webm_url)

    def _download(self, data):
        self._webm_url, md5 = data[0], data[-1]
        try:
            self._webm_obj = Webm.increase_rating(md5)
            result = None, None, None
            scraper.inform(
                'Increase rating {}'.format(self._webm_url), level=scraper.WARNING)
            self._add_webm_url()
        except Webm.DoesNotExist:
            self._webm_obj = Webm(md5=md5)
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
            self._add_webm_url()

    def work(self, *args, **kwargs):
        return super().work(self.save)


if __name__ == '__main__':
    sections = ['vg', 'b', 'a', 'mov']
    worker = scraper.MainWorker(sections, downloader=DownloadToModel)
    worker.work()
