import os
import sys

import http.client as http
import queue

import json
import time
import threading

from datetime import datetime


NETWORK_ERRORS = http.HTTPException, ConnectionError, OSError

BOARD_URL = '2ch.hk'
DEFAULT_SECTION = 'b'
CATALOG_URL = '/{}/catalog.json'
THREAD_URL = '/{}/res/{}.json'
RESOURCE_URL = '/{}/{}'

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    'Accept-Charset': 'utf-8',
}


INFO, WARNING, ERROR = 3, 2, 1
VERBOSITY_LEVEL = INFO
WEBM = 6

CONSOLE_COLORS = {
    INFO: '\033[0m',
    WARNING: '\033[93m',
    ERROR: '\033[91m',
    'HEADER': '\033[95m',
    'OKGREEN': '\033[92m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}


DONE = 1


def inform(msg, level=10):

    if level <= VERBOSITY_LEVEL:
        print(msg)
        # print('{}{}{}'.format(CONSOLE_COLORS[level], msg, CONSOLE_COLORS['ENDC']))


class Connection(object):

    def __init__(self, host=BOARD_URL):
        self._host = host
        self._connect()

    def _repeat_on(exceptions):
        def _repeat_on_error(function):
            def _f(self, *args, **kwargs):
                while True:
                    try:
                        return function(self, *args, **kwargs)
                    except exceptions as e:
                        inform(e, level=WARNING)
                        self._connect()
                        time.sleep(1)
            return _f
        return _repeat_on_error

    @_repeat_on(NETWORK_ERRORS)
    def _connect(self):
        self._conn = http.HTTPSConnection(self._host)
        self._set_headers()
        inform('Connected to {}'.format(self._host), level=INFO)

    def _set_cookie(self):
        resp = self.get_response('/')
        self._headers['Cookie'] = resp.getheader('set-cookie')
        resp.read()

    def _set_headers(self):
        self._headers = HEADERS

    @_repeat_on(NETWORK_ERRORS)
    def _get_response(self, request):
        inform('Requesting {}'.format(request), level=INFO)
        self._conn.request('GET', request, headers=self._headers)
        resp = self._conn.getresponse()
        inform('Response is {}: {}'.format(
            resp.status, resp.reason), level=INFO)
        return resp

    def get_response(self, request):
        return self._get_response(request)

    def get_json(self, request):
        json_data = {}

        resp = self._get_response(request)
        data = resp.read()

        try:
            data = data.decode('utf8')
        except (AttributeError, UnicodeDecodeError):
            pass

        if resp.status == 200:
            try:
                json_data = json.loads(data)
            except ValueError as e:
                inform(e, level=WARNING)
            except TypeError as e:
                inform(e, level=WARNING)

        return resp.status, json_data

    def get_file(self, request):
        return self._get_response(request).read()


def get_threads(connection, section):
    threads = []
    url = CATALOG_URL.format(section)
    status, catalog = connection.get_json(url)

    if status != 200:
        return threads

    try:
        threads = catalog['threads']
    except KeyError as e:
        inform('{}; KeyError: {}'.format(threads.keys(), e), level=WARNING)
        return threads

    for i, thread in enumerate(threads):
        threads[i] = THREAD_URL.format(section, thread['num'])

    return threads


def get_webms_from_thread(connection, host_url, section, thread_url):
    found_webms = 0
    webms = []
    base_url = '/'.join((host_url, section))
    status, data = connection.get_json(thread_url)
    if status != 200:
        return webms

    try:
        posts = data['threads'][0]['posts']
    except KeyError as e:
        inform('{}; KeyError: {}'.format(data.keys(), e), level=WARNING)
        return webms

    for post in posts:
        try:
            files = post['files']
        except KeyError:
            continue

        for f in files:
            if f.get('type', None) == WEBM:
                found_webms += 1
                url = '{}/{}'.format(base_url, f['path'])
                thumb = '{}/{}'.format(base_url, f['thumbnail'])
                md5 = f['md5']
                size = f['size']
                webms.append(Webm(url, thumb, md5, size))

    inform('Found {} webms'.format(found_webms), level=INFO)
    return webms


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


def get_webms(url=BOARD_URL, section=DEFAULT_SECTION):
    connection = Connection(url)
    webms = []
    threads = get_threads(connection, section)
    for thread_url in threads:
        new_webm = get_webms_from_thread(connection, url, section, thread_url)
        webms.extend(new_webm)

    return webms


def work(url, sections, webm_q, task_q):
    for s in sections:
        for w in get_webms(url, s):
            webm_q.put(w)

    task_q.put((DONE, sections))


def chunk_list(l, size):
    yield from [l[i:i + size] for i in range(0, len(l), size)]


if __name__ == '__main__':

    sections = ['a', 'abu', 'au', 'b', 'bg', 'bi', 'biz', 'bo',
                'c', 'cg', 'd', 'di', 'diy', 'e', 'em', 'es',
                'fa', 'fag', 'fd', 'fet', 'fg', 'fiz', 'fl',
                'ftb', 'fur', 'ga', 'gd', 'gg', 'h', 'hc',
                'hh', 'hi', 'ho', 'hw', 'ja', 'ma', 'me',
                'media', 'mg', 'mlp', 'mmo', 'mo', 'moba',
                'mobi', 'mov', 'mu', 'mus', 'ne', 'p', 'pa',
                'po', 'pr', 'psy', 'r', 'ra', 're', 'rf', 's',
                'sci', 'sex', 'sf', 'sn', 'soc', 'sp', 'spc',
                't', 'tes', 'trv', 'tv', 'un', 'vg', 'vn', 'w',
                'web', 'wh', 'wm', 'wn', 'wp', 'wr', 'wrk']

    url = BOARD_URL

    workers = 5
    webm_q = queue.Queue()
    task_q = queue.Queue()
    start = time.time()

    for sections_chunk in chunk_list(sections, len(sections) // workers):
        t = threading.Thread(
            target=work, args=(url, sections_chunk, webm_q, task_q))
        t.start()
        print('Thread started')

    done_workers = 0

    while done_workers != workers:
        signal = task_q.get()
        if signal[0] == DONE:
            print(signal[1], '- Done')
            done_workers += 1

    end = int(time.time() - start)
    m, s = end // 60, end % 60
    print('Threaded version: {}m {}s'.format(m, s))

    start = time.time()
    for s in sections:
        get_webms(url, s)
    end = int(time.time() - start)
    m, s = end // 60, end % 60
    print('Single thread version: {}m {}s'.format(m, s))

    w = 0
    webms = []
    directory = os.path.realpath(os.path.dirname(__file__))
    while not webm_q.empty():
        webms.append(webm_q.get())
        w += 1

    with open(os.path.join(directory, 'webms.txt'), 'w') as f:
        f.write('\n'.join(map(str, webms)))

    end = int(time.time() - start)
    m, s = end // 60, end % 60
    print('Total: {}. Time: {}m {}s'.format(w, m, s))
