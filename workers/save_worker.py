from datetime import date

from utils.rabbitmq import ConsumerRabbitMQ
from db.crud import create_exchange_rates
from utils.settings import QUEUE_DB_SAVE_NAME
from utils.logger_setup import get_logger

logger = get_logger("SAVE_WORKER")

def handle_save_task(message: dict, ch, method):
    """
    Handles a single database save task by validating the message payload and storing exchange rates into the database

    :param message: Message payload containing exchange rate data and metadata
    :param ch: RabbitMQ channel used to acknowledge the message
    :param method: Delivery metadata required for manual message acknowledgment
    :return: None
    """
    try:
        if not isinstance(message, dict):
            logger.error(f"Instead of the expected dict, we got: {type(message)}")
            raise ValueError("Очікувалось отримати dict, отримали: {type(message)}")

        if message.get("task_type") != "save_rates":
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        bank = message.get("bank")
        rates_data = message.get("rates_data")
        rate_date_str = message.get("rate_date")
        request_id = message.get("request_id")
        rate_date_obj: date = date.fromisoformat(rate_date_str)

        create_exchange_rates(
            bank=bank,
            rates_data=rates_data,
            rate_date=rate_date_obj,
            request_id=request_id,
        )

        logger.info(f"Data successfully saved to database: bank={bank}, rate_date={rate_date_str}, request_id={request_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == "__main__":
    consumer = ConsumerRabbitMQ()
    consumer.start(
        queue_name=QUEUE_DB_SAVE_NAME,
        callback=handle_save_task,
        durable=True,
        prefetch_count=1,
        auto_ack=False,
    )
