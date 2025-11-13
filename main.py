import logging
import uuid
from datetime import datetime

from api_logic import get_currency_exchange_rates
from parser import parse_arguments
from currency_output import format_currency_data

from logger_setup import logger


if __name__ == '__main__':
    # req_id = str(uuid.uuid4())
    args = parse_arguments()
    vcc = args.vcc if args.vcc else None
    res = get_currency_exchange_rates(valcode=vcc, date=args.currency_date)

    if res is None:
        logger.error("Помилка при обробці. res порожній")
        print("Error with request")
    else:
        logger.info(f"Запрошений курс валюти {res}")
        output = format_currency_data(res, datetime.strptime(args.currency_date, '%Y%m%d'))
        for i in output:
            print(i)
            print("-----")

