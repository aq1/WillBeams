import os
import sys

import http.client as http
import queue

import json
import time
import threading

from datetime import datetime

import pika


NETWORK_ERRORS = http.HTTPException, ConnectionError, OSError

BOARD_URL = '2ch.hk'
DEFAULT_SECTIONS = ['b', 'vg']
CATALOG_URL = '/{}/catalog.json'
THREAD_URL = '/{}/res/{}.json'
RESOURCE_URL = '/{}/{}'

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    'Accept-Charset': 'utf-8',
}


INFO, WARNING, ERROR, IMPORTANT_INFO = 3, 2, 1, 1
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

SECTIONS = ['a', 'abu', 'au', 'b', 'bg', 'bi', 'biz', 'bo',
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

DONE = 1
STOP_SIGNAL = 'Stop there'
WORKERS = 5


def inform(msg, level=10):

    if level <= VERBOSITY_LEVEL:
        print('{}{}{}'.format(CONSOLE_COLORS[level], msg, CONSOLE_COLORS['ENDC']))


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
        self._url = THREAD_URL.format(section, number)

    def get_webms(self, fetch_tool):
        inform('Searching for webms. Last post: {}'.format(self._last_post), level=INFO)
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
            inform('Key error: {}'.format(e), level=WARNING)
            return webms

        for post in posts:

            if post['num'] <= self._last_post:
                continue

            try:
                files = post['files']
            except KeyError:
                continue

            for f in files:
                if f.get('type', None) == WEBM:
                    found_webms_count += 1
                    url = RESOURCE_URL.format(self._section, f['path'])
                    thumb = RESOURCE_URL.format(self._section, f['thumbnail'])
                    md5 = f['md5']
                    size = f['size']
                    webms.append(Webm(url, thumb, md5, size))

        inform('Found {} webms'.format(found_webms_count), level=INFO)
        self._last_post = data['threads'][0]['posts'][-1]['num']
        return webms

    def __str__(self):
        return self._url


class Catalog:

    def __init__(self, section):

        self._url = CATALOG_URL.format(section)
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
            inform('{} {} {}'.format(e, threads.keys(), self._url), level=WARNING)
            return result

        for thread in threads:
            number = int(thread['num'])
            if number not in self._threads:
                result.append(Thread(self._section, number))
                self._threads.add(number)

            alive_threads.add(number)

        inform('Found {} threads'.format(len(result)), level=INFO)
        self._threads = alive_threads
        return result

    def __str__(self):
        return self._url


def print_output(webm):
    inform(webm, level=INFO)


def check_task_q(task_q):
    try:
        task = task_q.get(timeout=0.1)
    except queue.Empty:
        return None
    else:
        if task == STOP_SIGNAL:
            inform("I'm done", level=IMPORTANT_INFO)
            exit()


def work(task_q, url=BOARD_URL, sections=DEFAULT_SECTIONS, callback=print_output):
    connection = Connection(url)

    rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(
        'localhost'))
    channel = rabbitmq.channel()
    channel.queue_declare(queue='webm')

    catalogs = [Catalog(section=section) for section in sections]
    threads = []

    while True:
        for catalog in catalogs:
            check_task_q(task_q)

            threads.extend(catalog.get_threads(connection.get_json))

        for thread in threads:
            check_task_q(task_q)

            for webm in thread.get_webms(connection.get_json):
                callback(channel, webm)


def chunk_list(l, size):
    yield from [l[i:i + size] for i in range(0, len(l), size)]


def start_threads(task_q, workers, url, sections, callback):
    for sections_chunk in chunk_list(sections, len(sections) // workers):
        t = threading.Thread(
            target=work, args=(task_q, url, sections_chunk, callback))
        t.start()
        inform('Thread started', level=IMPORTANT_INFO)


def stop_threads(task_q, workers):
    for _ in range(workers):
        task_q.put(STOP_SIGNAL)


def put_into_rabbitmq(channel, webm):
    channel.basic_publish(exchange='',
                          routing_key='webm',
                          body=str(webm))


if __name__ == '__main__':
    task_q = queue.Queue()
    start_threads(task_q, WORKERS, BOARD_URL, SECTIONS, callback=put_into_rabbitmq)
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        inform('Stopping threads', level=IMPORTANT_INFO)
        stop_threads(task_q, WORKERS)
