from datetime import datetime

from api.api_logic import get_currency_exchange_rates
from utils.parser import parse_arguments
from utils.currency_output import format_currency_data

from db.db import connect
from utils.logger_setup import get_logger
logger = get_logger("CLI")


if __name__ == '__main__':
    connect()
    # req_id = str(uuid.uuid4())
    args = parse_arguments()
    vcc = args.vcc if args.vcc else None
    res = get_currency_exchange_rates(bank=args.bank, valcode=vcc, date=args.currency_date)

    if res is None:
        logger.error("Помилка при обробці. res порожній")
        print("Error with request")
    else:
        logger.info(f"Запрошений курс валюти {res}")
        output = format_currency_data(res, datetime.strptime(args.currency_date, '%Y%m%d'), args.bank, args.vcc)
        for i in output:
            print(i)
            print("-------")

