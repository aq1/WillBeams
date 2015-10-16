###Scrapper

Весь скрапер запускается с помощью файла main.py. Правда пока работает только парсер.

####Parser

Может работать как отдельным процессом (если запустить `python3 parser.py`) или же в треде - функция `start_thread(task_q, webm_q, url, sections)`. Параметры: task_q - обычная очередь питона, если туда положить utils.STOP_SIGNAL, то треды потихоньку остановятся. webm_q - канал для связи с rabbitmq, туда отправляется информация. sections - список разделов, за которыми надо следить.

Ну а посмотреть содержимое очереди можно с помощью какого нибудь скрипта типа:

```python
import pika

con = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = con.channel()
channel.queue_declare(queue='webm')

channel.basic_consume(lambda ch, method, properties, body: print(body),
                      queue='webm',
                      no_ack=True)
channel.start_consuming()
```

Из очереди ничего не пропадет.
