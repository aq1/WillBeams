import http.client as http
import json

import time

import utils


NETWORK_ERRORS = http.HTTPException, ConnectionError, OSError

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    'Accept-Charset': 'utf-8',
}


class Connection(object):

    def __init__(self, host=utils.BOARD_URL):
        self._host = host
        self._connect()

    def _repeat_on(exceptions):
        def _repeat_on_error(function):
            def _f(self, *args, **kwargs):
                while True:
                    try:
                        return function(self, *args, **kwargs)
                    except exceptions as e:
                        utils.inform(e, level=utils.WARNING)
                        self._connect()
                        time.sleep(1)
            return _f
        return _repeat_on_error

    @_repeat_on(NETWORK_ERRORS)
    def _connect(self):
        self._conn = http.HTTPSConnection(self._host)
        self._set_headers()
        utils.inform('Connected to {}'.format(self._host), level=utils.INFO)

    def _set_cookie(self):
        resp = self.get_response('/')
        self._headers['Cookie'] = resp.getheader('set-cookie')
        resp.read()

    def _set_headers(self):
        self._headers = HEADERS

    @_repeat_on(NETWORK_ERRORS)
    def _get_response(self, request):
        utils.inform('Requesting {}'.format(request), level=utils.INFO)
        self._conn.request('GET', request, headers=self._headers)
        resp = self._conn.getresponse()
        utils.inform('Response is {}: {}'.format(
            resp.status, resp.reason), level=utils.INFO)
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
                utils.inform(e, level=utils.WARNING)
            except TypeError as e:
                utils.inform(e, level=utils.WARNING)

        return resp.status, json_data

    def get_file(self, request):
        return self._get_response(request).read()
