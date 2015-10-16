'''
uniq = UnicheckClient(connection)
if uniq.call('check', 'md5', b'<some_md5>'):
    # already exists, dropping
else:
    uniq.call('put', 'md5', b'<some_md5>')
    # new value written into db
'''

import pickle
from ..rabbit import rpc_server, rabbit_main, AbstractRpcClient
from ..config import UNICHECK_QUEUE_NAME

from .md5 import check_keys as md5_check_keys, put_keys as md5_put_keys


def validate_check(value):
    assert isinstance(value, set)
    for k in value:
        assert isinstance(k, bytes)


def validate_put(value):
    assert isinstance(value, dict)
    for k, v in value.items():
        assert isinstance(k, bytes)
        assert isinstance(v, bytes)


available_ways = {
    'md5': (md5_check_keys, md5_put_keys),
}
METHODS = ('check', 'put')
VAL_FUNCS = (validate_check, validate_put)


@rabbit_main
def run_server(connection, storage):

    def serialize_response(v):
        return pickle.dumps(v)

    def deserialize_request(v):
        return pickle.loads(v), {}

    with storage as st:

        def handler(method, way, value):
            if method not in METHODS or way not in available_ways:
                return None
            mi = METHODS.index(method)
            try:
                VAL_FUNCS[mi](value)
            except AssertionError:
                return None
            func = available_ways[way][mi]
            return func(st, value)

        rpc_server(
            connection,
            handler,
            serialize_response,
            deserialize_request,
            queue_name=UNICHECK_QUEUE_NAME
        )


class UnicheckClient(AbstractRpcClient):
    QUEUE_NAME = UNICHECK_QUEUE_NAME

    def serialize_request(self, method, way, value):
        return pickle.dumps((method, way, value))

    def deserialize_response(self, resp):
        return pickle.loads(resp)
