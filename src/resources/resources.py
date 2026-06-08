import pika
import pika.exceptions
import os
import time
import logging

LOG = logging.getLogger(__name__)

def rabbitmq_connect(host: str = os.environ.get('RABBITMQ_HOST', 'rabbitmq'), queue_name: str = 'default'):
    delay = 2
    for attempt in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            if attempt < 9:
                LOG.warning(f'RabbitMQ not ready, retrying in {delay}s... ({attempt + 1}/10)')
                time.sleep(delay)
                delay = min(delay * 2, 30)
            else:
                raise
