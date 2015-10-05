import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='webm')


def callback(ch, method, properties, body):
    print(body)


channel.basic_consume(callback,
                      queue='webm',
                      no_ack=True)

channel.start_consuming()
