import os
import uuid
import time
import json
import pika
from typing import Dict, Any, Optional

from utils.logger_setup import get_logger
from db.crud import create_exchange_rates

logger = get_logger("RABBITMQ")


class PublisherRabbitMQ:
    """
    Універсальний паблішер
    """
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    def send(self, message: dict, queue_name: str, durable: bool = True):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            channel = connection.channel()

            channel.queue_declare(queue=queue_name, durable=durable)

            body = json.dumps(message)

            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)
            )

            logger.info(f"Повідомлення надіслано в чергу '{queue_name}': {message}")
            connection.close()

        except Exception as e:
            logger.error(f"Помилка надсилання: {e}")
            raise

class ConsumerRabbitMQ:
    """
    Універсальний консюмер
    """
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    def start(
        self,
        queue_name: str,
        callback,
        durable: bool = True,
        prefetch_count: int = 1,
        auto_ack: bool = False
    ):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            channel = connection.channel()

            channel.queue_declare(queue=queue_name, durable=durable)

            channel.basic_qos(prefetch_count=prefetch_count)

            def on_message(ch, method, properties, body):
                message = json.loads(body)
                logger.info(f"Отримано з '{queue_name}': {message}")

                callback(message, ch, method)

                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message,
                auto_ack=auto_ack
            )

            logger.info(f"Слухач запущено на черзі '{queue_name}'")
            channel.start_consuming()

        except Exception as e:
            logger.info("Слухач зупинено")
        finally:
            if connection:
                connection.close()

class PublisherRPCRabbitMQ:
    """
    Паблішер + rpc
    """

    def __init__(self, host: Optional[str] = None):
        self._host = host

    @property
    def host(self):
        if self._host is None:
            self._host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        return self._host

    def call(self, routing_key: str, request_body: dict, timeout: float = 30.0):
        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            channel = connection.channel()

            result = channel.queue_declare(queue='', exclusive=True)
            callback_queue = result.method.queue

            corr_id = str(uuid.uuid4())
            response = None

            def on_response(ch, method, props, body):
                nonlocal response
                if corr_id == props.correlation_id:
                    try:
                        decoded = body.decode('utf-8')
                        response = json.loads(decoded)
                    except Exception as e:
                        logger.error(f"Помилка розпарсингу: {e}")
                        response = {"status": "error", "error": str(e)}

            channel.basic_consume(
                queue=callback_queue,
                on_message_callback=on_response,
                auto_ack=True
            )

            body = json.dumps(request_body)

            channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                properties=pika.BasicProperties(
                    reply_to=callback_queue,
                    correlation_id=corr_id,
                ),
                body=body
            )

            logger.info(f"Надіслано запит до '{routing_key}'")

            start = time.time()
            while response is None:
                connection.process_data_events(time_limit=0.1)
                if time.time() - start > timeout:
                    logger.warning(f"RPC таймаут після {timeout} секунд")
                    return None

            return response

        except Exception as e:
            logger.error(f"Помилка RPC: {e}")
            return None
        finally:
            if connection:
                connection.close()


class ConsumerRPCRabbitMQ:
    """
    Консюмер + rpc
    """
    def __init__(self, queue_name: str, host="rabbitmq"):
        self.queue_name = queue_name
        self.host = host

    def start(self, callback):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)

        def on_request(ch, method, props, body):
            try:
                request = json.loads(body)
                response = callback(request)

                ch.basic_publish(
                    exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(correlation_id=props.correlation_id),
                    body=json.dumps(response)
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Помилка RPC: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue=self.queue_name, on_message_callback=on_request)
        logger.info(f"RPC сервер запущено на {self.queue_name}")
        channel.start_consuming()
