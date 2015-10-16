import pika
from . import config


def rabbit_main(func):
    def inner(*args, **kwargs):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(**config.PIKA_PARAMETERS)
        )
        try:
            func(connection, *args, **kwargs)
        finally:
            connection.close()
    return inner


def simple_putter(connection, serialize, *, queue_name, durable=False):
    channel = connection.channel()
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


def simple_getter(connection, deserialize, handler, *, queue_name, durable=False, no_ack=False):
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=durable)
    channel.basic_qos(prefetch_count=1)  # don't use round robin dispatching

    def msg_callback(ch, method, properties, body):
        args, kwargs = deserialize(body)
        result = handler(*args, **kwargs)  # must return True on success
        if not no_ack and result:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    for method, props, body in channel.consume(
        queue=queue_name, no_ack=no_ack, exclusive=True
    ):
        msg_callback(channel, method, props, body)


def rpc_server(connection, remote_procedure, serialize_response, deserialize_request, *, queue_name):
    channel = connection.channel()
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

    def __init__(self, connection):
        self.connection = connection
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.auto_id = 1

    def _allocate_id(self):
        r = format(self.auto_id, 'x')
        self.auto_id += 1
        return r

    def call(self, *args, **kwargs):
        corr_id = self._allocate_id()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.QUEUE_NAME,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
            ),
            body=self.serialize_request(*args, **kwargs)
        )
        for method, props, body in self.channel.consume(
            queue=self.callback_queue, no_ack=True, exclusive=True
        ):
            # docs notice that same id can arrive twice, don't assert check id
            if corr_id == props.correlation_id:
                break
        return self.deserialize_response(body)
