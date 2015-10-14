import pika
from . import config


def rabbit_main(func):
    def inner(*args, **kwargs):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(**config.PIKA_PARAMETERS)
        )
        channel = connection.channel()
        try:
            func(connection, channel, *args, **kwargs)
        finally:
            connection.close()
    return inner


def simple_putter(connection, channel, serialize, *, queue_name, durable=False):
    channel.queue_declare(queue=queue_name, durable=durable)
    kw = {}
    if durable:
        kw['properties'] = pika.BasicProperties(delivery_mode=2)

    def put_fn(*args, **kwargs):
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=serialize(*args, **kwargs),
            **kw
        )
    return put_fn


def simple_getter(connection, channel, deserialize, handler, *, queue_name, durable=False, no_ack=False):
    channel.queue_declare(queue=queue_name, durable=durable)
    channel.basic_qos(prefetch_count=1)  # don't use round robin dispatching

    def msg_callback(ch, method, properties, body):
        result = handler(deserialize(body))  # must return True on success
        if not no_ack and result:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(msg_callback, queue=queue_name, no_ack=no_ack)
    channel.start_consuming()


def rpc_server(channel, remote_procedure, serialize_response, deserialize_request, *, queue_name):
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        args, kwargs = deserialize_request(body)
        response = serialize_response(remote_procedure(*args, **kwargs))
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queue_name)
    channel.start_consuming()


class AbstractRpcClient:
    QUEUE_NAME = None  # override in descendant

    def serialize_request(self, *args, **kwargs):
        raise NotImplemented

    def deserialize_response(self, resp):
        raise NotImplemented

    def __init__(self, connection, channel):
        self.connection = connection
        self.channel = channel
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)
        self.auto_id = 1

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def _allocate_id(self):
        r = format(self.auto_id, 'x')
        self.auto_id += 1
        return r

    def call(self, *args, **kwargs):
        self.response = None
        self.corr_id = self._allocate_id()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.QUEUE_NAME,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=self.serialize_request(*args, **kwargs)
        )
        while self.response is None:
            self.connection.process_data_events()
        resp = self.deserialize_response(self.response)
        self.response = None
        return resp
