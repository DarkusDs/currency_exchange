import argparse
import logging
from typing import Optional, List, Dict
from urllib.error import URLError

import requests
from datetime import datetime

from requests.exceptions import URLRequired, HTTPError, ConnectionError


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def validate_date(date: str) -> bool:
    """
    Validate input date for compliance with the format YYYYMMDD

    :param date:
    :return:
    """
    try:
        datetime.strptime(date, '%Y%m%d')
        return True
    except ValueError:
        return False

def get_currency_exchange_rates(date: str, valcode: str, type: str = "json") -> Optional[List[Dict]]:
    """
    Send request for api and parse result

    :param date:
    :param valcode:
    :param type:
    :return:
    """
    res = None

    try:
        url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
        params = {
            'valcode': valcode,
            'date': date,
            'type': type
        }
        res = requests.get(url, params=params)
        res = res.json()
        logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
    except HTTPError as e:
        logger.error("HTTP Error")
    except ConnectionError as e:
        logger.error("ConnectionError")
    except URLRequired as e:
        logger.error("URLRequired")
    except Exception as e:
        logger.error(e)
    finally:
        return res

def parse_arguments():
    """
    Parse command line arguments

    :return:
    """
    parser = argparse.ArgumentParser(description='Currency Exchange')
    parser.add_argument('--vcc',
                        type=str,
                        default='',
                        help='tag for currency code, if not specified, will show all currency types', )

    parser.add_argument('--currency_date',
                        type=str,
                        default=datetime.today().strftime('%Y%m%d'),
                        help='tag for currency date, if not specified, will show currency rate for current date. Input format: YYYYMMDD')
    if not validate_date(args.currency_date):
        print("Дата введена в неправильному форматі. Потрібен формат YYYYMMDD")
        logger.error("Помилка при введенні дати, формат невірний")

    logger.info("Парсинг аргументів завершено")
    return parser.parse_args()


if __name__ == '__main__':
#TODO: ПОДУМАТИ як оформити результат
    args = parse_arguments()
    res = get_currency_exchange_rates(valcode=args.vcc, date=args.currency_date)

    if res is None:
        logger.error("Помилка при обробці. res порожній")
        print("Error with request")
    else:
        logger.info(f"Запрошений курс валюти {res}")
        print(res)
