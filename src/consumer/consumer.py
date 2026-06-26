import logging
import json
import time

from prometheus_client import Counter, Histogram, start_http_server

from heudb.db import Database
from resources.resources import rabbitmq_connect

DESIRED_KEYS = ['attributes', 'legacy']
LOG_FORMAT = '%(asctime)s;%(levelname)s;%(message)s'
LOG = logging.getLogger(__name__)

MESSAGES_PROCESSED = Counter(
    'messages_processed_total',
    'Total number of messages successfully processed'
)
MESSAGES_FAILED = Counter(
    'messages_failed_total',
    'Total number of messages that failed processing'
)
DB_INSERTS = Counter(
    'db_inserts_total',
    'Total number of database inserts',
    ['table']
)
MESSAGE_PROCESSING_TIME = Histogram(
    'message_processing_seconds',
    'Time spent processing a single message'
)

class Consumer():

    def __init__(self, db: Database, queue_name: str = 'default'):
        self.db = db
        self.connection, self.channel = rabbitmq_connect(queue_name=queue_name)
        LOG.info('RabbitMQ channel opened.')

    @staticmethod
    def parse_on_receive(channel, method, properties, body):
        db = Database()

        def _crawl_recursively(data: dict, match: str, id: str) -> tuple:
            last_id = id
            for key, val in data.items():
                if key == 'id':
                    last_id = val
                if key == match:
                    yield last_id, val
                elif isinstance(val, dict):
                    for sub_dict in _crawl_recursively(val, match, last_id):
                        yield last_id, sub_dict
                elif isinstance(val, list):
                    for element in val:
                        if isinstance(element, dict):
                            for el in _crawl_recursively(element, match, last_id):
                                yield last_id, el

        start = time.time()
        try:
            msg_dict = json.loads(body.decode('utf-8'))
            for item in DESIRED_KEYS:
                for _, val in _crawl_recursively(msg_dict, item, ''):
                    if val[1]:
                        db.insert_offer(val[0])
                        DB_INSERTS.labels(table='offers').inc()
                        match item:
                            case 'attributes':
                                db.insert_attributes(offer_id=val[0], attributes_list=val[1])
                                DB_INSERTS.labels(table='attributes').inc()
                            case 'legacy':
                                db.insert_legacy(val[0], val[1])
                                DB_INSERTS.labels(table='legacy').inc()
                            case _:
                                LOG.warning('Unrecognized key!')
            MESSAGES_PROCESSED.inc()
        except Exception as e:
            MESSAGES_FAILED.inc()
            LOG.error(f'Failed to process message: {e}')
        finally:
            MESSAGE_PROCESSING_TIME.observe(time.time() - start)

    def start_consuming(self, queue_name: str, auto_ack: str = True) -> None:
        self.channel.basic_consume(on_message_callback=self.parse_on_receive,
                                   queue=queue_name,
                                   auto_ack=auto_ack)
        LOG.info('Consumer initiated.')
        LOG.info('Consumer started. Waiting for messages.\n...')
        self.channel.start_consuming()

def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    start_http_server(8000)
    LOG.info('Prometheus metrics server started on port 8000.')
    db = Database()
    db.create_tables()
    consumer = Consumer(db=db)
    consumer.start_consuming('default')

if __name__ == "__main__":
    main()
