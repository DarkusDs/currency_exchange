import sys
import os

import json

import pika

from utils.rabbitmq import ConsumerRPCRabbitMQ
from utils.rabbitmq import PublisherRabbitMQ
from api.api_logic import get_currency_exchange_rates
from utils.currency_output import format_currency_data
from datetime import datetime
from utils.logger_setup import get_logger

from utils.settings import QUEUE_REQUEST_NAME, QUEUE_DB_SAVE_NAME
from utils.currency_names import get_display_name

logger = get_logger("REQUEST_PROCESSOR")

def process_request(message: dict):
    if message.get("task_type") != "get_rates":
        return {"status": "error", "error": "Невідомий тип задачі"}

    bank = message["bank"]
    date = message["date"]
    valcode = message.get("valcode")
    request_id = message["request_id"]

    try:
        raw_data = get_currency_exchange_rates(bank=bank, date=date, valcode=valcode)
        if not raw_data:
            raise ValueError("Не вдалося отримати курси від банку")
        date_obj = datetime.strptime(date, "%Y%m%d")
        date_response = date_obj.strftime("%d-%m-%Y")

        formated_data = format_currency_data(raw_data, date_obj, bank, valcode)

        rates_list = []
        for i in formated_data:
            rate = i.rate
            if rate is None:
                continue


        text = f"Курс валют на {date_response} ({bank.upper()}): \n---------------\n"
        for i in formated_data:
            rate = i.rate
            if rate is None:
                continue
            name = i.name
            code = None
            for c in raw_data:
                if c.get("name") == i.name:
                    code = c.get('code')
                    break


            display_name = get_display_name(code, i.name)

            rates_list.append({
                "name": display_name,
                "code": code,
                "rate": rate,
                "date": i.date.strftime("%Y-%m-%d"),
            })

            text += f"{code} - {display_name} - {rate} \n-----\n"
        PublisherRabbitMQ().send(
            {
                "task_type": "save_rates",
                "bank": bank,
                "rates_data": raw_data,
                "rate_date": date_obj.date().isoformat(),
                "request_id": request_id
            },
            queue_name=QUEUE_DB_SAVE_NAME
        )

        return {
            "status": "success",
            "request_id": request_id,
            "text": text,
            "bank": bank,
            "date": date,
            "requested_currency": valcode or "всі",
            "rates": rates_list
        }

    except Exception as e:
        logger.error(f"Помилка обробки запиту {request_id}: {e}")
        return {
            "status": "error",
            "request_id": request_id,
            "error": str(e)
        }

if __name__ == "__main__":
    consumer = ConsumerRPCRabbitMQ(queue_name=QUEUE_REQUEST_NAME)
    consumer.start(process_request)
