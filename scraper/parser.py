import threading

import qhandler
import utils
from connection import Connection


class Webm:

    def __init__(self, url, thumb, md5, size):
        self.url = url
        self.thumb = thumb
        self.md5 = md5
        self.size = size

    def __repr__(self):
        return 'Webm(url={}, thumb={}, md5={}, size={})'.format(self.url,
                                                                self.thumb,
                                                                self.md5,
                                                                self.size)

    def __str__(self):
        return '{} {} {} {}'.format(self.url, self.thumb, self.md5, self.size)


class Thread:

    def __init__(self, section, number):
        self._section = section
        self._last_post = 0
        self._url = utils.THREAD_URL.format(section, number)

    def get_webms(self, fetch_tool):
        utils.inform('Searching for webms. Last post: {}'.format(
            self._last_post), level=utils.INFO)
        webms = []
        status, data = fetch_tool(self._url)

        if status == 404:
            return None
        elif status != 200:
            return webms

        found_webms_count = 0
        try:
            posts = data['threads'][0]['posts']
        except KeyError as e:
            utils.inform('Key error: {}'.format(e), level=utils.WARNING)
            return webms

        for post in posts:

            if post['num'] <= self._last_post:
                continue

            try:
                files = post['files']
            except KeyError:
                continue

            for f in files:
                if f.get('type', None) == utils.WEBM:
                    found_webms_count += 1
                    url = utils.RESOURCE_URL.format(self._section, f['path'])
                    thumb = utils.RESOURCE_URL.format(self._section, f['thumbnail'])
                    md5 = f['md5']
                    size = f['size']
                    webms.append(Webm(url, thumb, md5, size))

        utils.inform('Found {} webms'.format(found_webms_count), level=utils.INFO)
        self._last_post = data['threads'][0]['posts'][-1]['num']
        return webms

    def __str__(self):
        return self._url


class Catalog:

    def __init__(self, section):

        self._url = utils.CATALOG_URL.format(section)
        self._section = section
        self._threads = set()

    def get_threads(self, fetch_tool):
        alive_threads = set()
        result = []
        status, data = fetch_tool(self._url)

        if status != 200:
            return result

        try:
            threads = data['threads']
        except KeyError as e:
            utils.inform('{} {} {}'.format(e, threads.keys(), self._url), level=utils.WARNING)
            return result

        for thread in threads:
            number = int(thread['num'])
            if number not in self._threads:
                result.append(Thread(self._section, number))
                self._threads.add(number)

            alive_threads.add(number)

        utils.inform('Found {} threads'.format(len(result)), level=utils.INFO)
        self._threads = alive_threads
        return result

    def __str__(self):
        return self._url


def print_output(webm):
    utils.inform(webm, level=utils.INFO)


def work(task_q, webm_q, url=utils.BOARD_URL, sections=utils.DEFAULT_SECTIONS):
    connection = Connection(url)

    catalogs = [Catalog(section=section) for section in sections]
    threads = []

    while True:
        for catalog in catalogs:
            qhandler.check_task_q(task_q)

            threads.extend(catalog.get_threads(connection.get_json))

        # if thread is 404 we need to remove it from list
        i = 0
        length = len(threads)
        while i < length:
            qhandler.check_task_q(task_q)
            webms = threads[i].get_webms(connection.get_json)

            if webms is None:
                del threads[i]
                length -= 1
                continue

            i += 1
            for webm in webms:
                qhandler.put(webm_q, webm)


def start_thread(task_q, webm_q, url, sections):
    threading.Thread(target=work, args=(task_q, webm_q, url, sections)).start()
    utils.inform('Parser thread started', level=utils.IMPORTANT_INFO)


def stop_threads(task_q, workers):
    for _ in range(workers):
        task_q.put(utils.STOP_SIGNAL)


if __name__ == '__main__':
    task_q = qhandler.get_task_q()
    webm_q = qhandler.create_channel()
    url = utils.BOARD_URL
    sections = ['b']
    try:
        work(task_q, webm_q, url, sections)
    except (KeyboardInterrupt, SystemExit):
        utils.inform("I'm done", level=utils.IMPORTANT_INFO)
        exit()
