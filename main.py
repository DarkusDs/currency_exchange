from datetime import datetime

from api.api_logic import get_currency_exchange_rates
from utils.parser import parse_arguments
from utils.currency_output import format_currency_data
from utils.rabbitmq import PublisherRPCRabbitMQ
from utils.settings import QUEUE_REQUEST_NAME
from uuid import uuid4

from db.db import connect
from utils.logger_setup import get_logger
logger = get_logger("CLI")

def main():
    args = parse_arguments()
    bank = args.bank
    date = args.currency_date
    vcc = args.vcc.upper() if args.vcc else None
    request_id = f"CLI_{uuid4().hex[:8]}"

    request = {
        "task_type": "get_rates",
        "bank": bank,
        "date": date,
        "valcode": vcc,
        "request_id": request_id
    }

    rpc = PublisherRPCRabbitMQ()
    response = rpc.call(
        routing_key=QUEUE_REQUEST_NAME,
        request_body=request,
        timeout=20.0,
    )

    if response is None:
        logger.error(f"Timeout: {request_id}")
        return

    if not isinstance(response, dict):
        logger.error(f"Некоректна відповідь воркеру: {response}")
        return

    if response.get("status") != "success":
        logger.error("Помилка обробки запиту")
        return

    text = response.get("text", "")
    if text:
        print(text)
        return

    rates = response.get("rates", [])
    if not rates:
        print("Даних немає")
        return

    for rate in rates:
        print(f"{rate.get('code')} - {rate.get('name')} - {rate.get('rate')} - {rate.get('date')}")

if __name__ == '__main__':
    main()

    # connect()
    # # req_id = str(uuid.uuid4())
    # args = parse_arguments()
    # vcc = args.vcc if args.vcc else None
    # res = get_currency_exchange_rates(bank=args.bank, valcode=vcc, date=args.currency_date)
    #
    # if res is None:
    #     logger.error("Помилка при обробці. res порожній")
    #     print("Error with request")
    # else:
    #     logger.info(f"Запрошений курс валюти {res}")
    #     output = format_currency_data(res, datetime.strptime(args.currency_date, '%Y%m%d'), args.bank, args.vcc)
    #     for i in output:
    #         print(i)
    #         print("-------")

