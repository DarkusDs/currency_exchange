from datetime import datetime


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
