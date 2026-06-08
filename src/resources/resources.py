import pika
import os

def rabbitmq_connect(host: str = os.environ.get('RABBITMQ_HOST', 'rabbitmq'), queue_name: str = 'default'):
    """
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    return connection, channel

