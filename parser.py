import argparse, logging
from datetime import datetime

from date_logic import validate_date
from logger_setup import logger


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
    args = parser.parse_args()

    if not validate_date(args.currency_date):
        print("Дата введена в неправильному форматі. Потрібен формат YYYYMMDD")
        logger.error("Помилка при введенні дати, формат невірний")
        exit()

    logger.info("Парсинг аргументів завершено")
    return parser.parse_args()
