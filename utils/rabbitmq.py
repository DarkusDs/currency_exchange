import os
import uuid
import time
import json
import pika
from typing import Optional

from utils.logger_setup import get_logger

logger = get_logger("RABBITMQ")


class PublisherRabbitMQ:
    """
    Simple RabbitMQ publisher that sends JSON messages to a specified queue
    """
    def __init__(self):
        """
        Initializes the publisher using the RabbitMQ host from environment variables
        """
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    def send(self, message: dict, queue_name: str, durable: bool = True):
        """
        Publishes a JSON-encoded message to the given queue with optional durability

        :param message: Message payload to be serialized as JSON
        :param queue_name: Target queue name to publish into
        :param durable: If True, declares the queue as durable and uses persistent delivery mode
        :return: None
        """
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

            logger.info(f"Message sent to queue '{queue_name}': {message}")
            connection.close()

        except Exception as e:
            logger.error(f"Sending error: {e}")
            raise

class ConsumerRabbitMQ:
    """
    Generic RabbitMQ consumer that listens to a queue and processes messages via a callback
    """
    def __init__(self):
        """
        Initializes the consumer using the RabbitMQ host from environment variables
        """
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    def start(
        self,
        queue_name: str,
        callback,
        durable: bool = True,
        prefetch_count: int = 1,
        auto_ack: bool = False
    ):
        """
        Starts consuming messages from a queue and passes each decoded JSON payload to the provided callback

        :param queue_name: Queue name to consume from
        :param callback: Function invoked for each message (message, channel, method)
        :param durable: If True, declares the queue as durable
        :param prefetch_count: Max number of unacked messages delivered to the consumer at once
        :param auto_ack: If True, messages are acknowledged automatically; otherwise manual ack is used
        :return: None
        """
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

            logger.info(f"Listener started on queue '{queue_name}'")
            channel.start_consuming()

        except Exception as e:
            logger.info("Слухач зупинено")
        finally:
            if connection:
                connection.close()

class PublisherRPCRabbitMQ:
    """
    RPC client over RabbitMQ that sends a request and waits for a correlated JSON response
    """

    def __init__(self, host: Optional[str] = None):
        """
        Creates an RPC client with an optional explicit host override

        :param host: Optional RabbitMQ host; if None, environment variable is used
        :return: None
        """
        self._host = host

    @property
    def host(self):
        """
        Resolves and returns the RabbitMQ host from configuration or environment

        :return: RabbitMQ host string
        """
        if self._host is None:
            self._host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        return self._host

    def call(self, routing_key: str, request_body: dict, timeout: float = 30.0):
        """
        Sends an RPC request to the given routing key and waits for a JSON response until timeout

        :param routing_key: Target queue/routing key for the RPC request
        :param request_body: Request payload to be serialized as JSON
        :param timeout: Max time to wait for the correlated response (seconds)
        :return: Response dictionary on success, or None on timeout/error
        """
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
                        logger.error(f"Parsing error: {e}")
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

            logger.info(f"Request sent to '{routing_key}'")

            start = time.time()
            while response is None:
                connection.process_data_events(time_limit=0.1)
                if time.time() - start > timeout:
                    logger.warning(f"RPC timeout after {timeout} seconds")
                    return None

            return response

        except Exception as e:
            logger.error(f"RPC Error: {e}")
            return None
        finally:
            if connection:
                connection.close()


class ConsumerRPCRabbitMQ:
    """
    RPC server over RabbitMQ that processes requests via a callback and replies to the provided reply_to queue
    """
    def __init__(self, queue_name: str, host="rabbitmq"):
        """
        Initializes the RPC consumer for a specific queue and RabbitMQ host

        :param queue_name: Queue name to listen for RPC requests
        :param host: RabbitMQ host name
        """
        self.queue_name = queue_name
        self.host = host

    def start(self, callback):
        """
        Starts the RPC server loop, passing each decoded request to the callback and publishing its result as a reply

        :param callback: Function that accepts a request dict and returns a response dict
        :return: None
        """
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
                logger.error(f"RPC error: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue=self.queue_name, on_message_callback=on_request)
        logger.info(f"RPC server started on {self.queue_name}")
        channel.start_consuming()
