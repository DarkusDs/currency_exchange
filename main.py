import logging
import uuid
from datetime import datetime

from api_logic import get_currency_exchange_rates
from parser import parse_arguments
from currency_output import format_currency_data

req_id = str(uuid.uuid4())
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(f"%(asctime)s - %(levelname)s - {req_id} - %(message)s")
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


if __name__ == '__main__':
    # req_id = str(uuid.uuid4())
    args = parse_arguments()
    vcc = args.vcc if args.vcc else None
    res = get_currency_exchange_rates(valcode=vcc, date=args.currency_date)

    if res is None:
        logging.error("Помилка при обробці. res порожній")
        print("Error with request")
    else:
        logging.info(f"Запрошений курс валюти {res}, ID: {req_id}")
        output = format_currency_data(res, datetime.strptime(args.currency_date, '%Y%m%d'))
        for i in output:
            print(i)
            print("-----")

