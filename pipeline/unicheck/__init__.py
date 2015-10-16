'''
from unicheck.md5 import PREFIX as md5_PREFIX
uniq = UnicheckClient(connection)
uniq.call('check', {
    md5_PREFIX + b'<some_md5>',
    md5_PREFIX + b'<some_md5>',
    ...
})
uniq.call('put', {
    md5_PREFIX + b'<some_md5>': b'<value>',
    md5_PREFIX + b'<some_md5>': b'<value>',
    ...
})
'''

import pickle
from ..rabbit import rpc_server, rabbit_main, AbstractRpcClient
from ..config import UNICHECK_QUEUE_NAME


def validate_check(value):
    assert isinstance(value, set)
    for k in value:
        assert isinstance(k, bytes)


def validate_put(value):
    assert isinstance(value, dict)
    for k, v in value.items():
        assert isinstance(k, bytes)
        assert isinstance(v, bytes)


def check_keys(kv, keys):
    return kv.get_many(set(keys))


def put_keys(kv, d):
    kv.put_many(d)
    return True


METHODS = {
    'check': (check_keys, validate_check),
    'put': (put_keys, validate_put),
}


@rabbit_main
def run_server(connection, storage):

    def serialize_response(v):
        return pickle.dumps(v)

    def deserialize_request(v):
        return pickle.loads(v), {}

    with storage as st:

        def handler(method, value):
            if method not in METHODS:
                return None
            func, val = METHODS[method]
            try:
                val(value)
            except AssertionError:
                return None
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

    def serialize_request(self, method, value):
        return pickle.dumps((method, value))

    def deserialize_response(self, resp):
        return pickle.loads(resp)
