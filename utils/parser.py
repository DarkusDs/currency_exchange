import argparse
from datetime import datetime

from utils.date_logic import validate_date
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")

def parse_arguments():
    """
    Parses and validates command-line arguments for the CLI currency exchange tool

    :return: Namespace object containing validated CLI arguments (bank, currency_date, vcc)
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
                        help=f'tag for choosing bank from wich you want get exchange rates')
    args = parser.parse_args()

    if not validate_date(args.currency_date):
        print("Дата введена в неправильному форматі. Потрібен формат YYYYMMDD")
        logger.error("Error entering date, format is incorrect")
        exit()

    logger.info(f"Argument parsing completed: {args}")
    return parser.parse_args()
