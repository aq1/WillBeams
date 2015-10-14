'''
uniq = UnicheckClient(connection, channel)
if uniq.call('check', 'md5', b'<some_md5>'):
    # already exists, dropping
else:
    uniq.call('put', 'md5', b'<some_md5>')
    # new value written into db
'''

import pickle
from ..rabbit import rpc_server, rabbit_main, AbstractRpcClient
from ..config import UNICHECK_QUEUE_NAME

from .md5 import check_key as md5_check_key, put_key as md5_put_key


available_ways = {
    'md5': (md5_check_key, md5_put_key),
}


@rabbit_main
def run_server(connection, channel, storage):

    def serialize_response(v):
        if v is None:
            return b''
        return b'Y' if v else b'N'

    def deserialize_request(v):
        return pickle.loads(v), {}

    with storage as st:

        def handler(method, way, value):
            meth_key = 1 if method == 'put' else 0
            func = available_ways[way][meth_key]
            return func(st, value)

        rpc_server(
            channel,
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
        if resp == b'':
            return None
        return resp == b'Y'
