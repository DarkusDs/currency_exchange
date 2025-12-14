import argparse
from datetime import datetime

from utils.date_logic import validate_date
from utils.logger_setup import logger
from settings import SupportedApi

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
    parser.add_argument('--bank',
                        type=str,
                        choices=['nbu', 'privat'],
                        default='nbu',
                        # choices=SupportedApi().as_list(),
                        # default=SupportedApi._nbu,
                        help=f'tag for choosing bank from wich you want get exchange rates {str(SupportedApi)}')
    args = parser.parse_args()

    if not validate_date(args.currency_date):
        print("Дата введена в неправильному форматі. Потрібен формат YYYYMMDD")
        logger.error("Помилка при введенні дати, формат невірний")
        exit()

    logger.info(f"Завершено парсинг аргументів: {args}")
    return parser.parse_args()
