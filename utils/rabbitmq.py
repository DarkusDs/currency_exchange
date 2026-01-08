import pika
import json
from datetime import datetime
from typing import Dict, Any

from utils.logger_setup import get_logger
from db.crud import create_exchange_rates

logger = get_logger("RABBITMQ")

RABBITMQ_HOST = 'rabbitmq'
QUEUE_NAME = 'currency_save_tasks'

def send_save_task(bank: str, rates_data: list, rate_date: str, request_id: str):
    task_data = {
        "task_type": "save_rates",
        "bank": bank,
        "rates_data": rates_data,
        "rate_date": rate_date,
        "request_id": request_id
    }

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(task_data),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()
    logger.info(f"Надіслано завдання на збереження в чергу. request_id: {request_id} | bank: {bank} | date: {rate_date}")


def _callback(ch, method, properties, body):
    try:
        task = json.loads(body)
        logger.info(f"Отримано завдання з черги. request_id: {task.get('request_id', 'N/A')}")

        if task.get("task_type") != "save_rates":
            logger.warning(f"Невідомий тип завдання: {task.get('task_type')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        rate_date_obj = datetime.fromisoformat(task["rate_date"]).date()

        create_exchange_rates(
            bank=task["bank"],
            rates_data=task["rates_data"],
            rate_date=rate_date_obj,
            request_id=task.get("request_id")
        )

        logger.info(
            f"Успішно збережено курси в БД. bank: {task['bank']}"
            f"date: {rate_date_obj}"
            f"request_id: {task.get('request_id')}"
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Помилка при обробці завдання з черги: {e} | body: {body}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_worker():
    logger.info("Запуск воркера RabbitMQ")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=_callback,
        auto_ack=False
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Воркер зупинено користувачем")
        connection.close()
