import queue

import pika

import utils


task_q = queue.Queue()


def get_task_q():
    return task_q


def check_task_q(task_q):
    try:
        task = task_q.get(timeout=0.1)
    except queue.Empty:
        return None
    else:
        if task == utils.STOP_SIGNAL:
            utils.inform("I'm done", level=utils.IMPORTANT_INFO)
            exit()


def put(channel, webm):
    channel.basic_publish(exchange='',
                          routing_key='webm',
                          body=str(webm))


def create_channel(host='localhost', queue_name='webm'):
    con = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = con.channel()
    channel.queue_declare(queue=queue_name)

    return channel
