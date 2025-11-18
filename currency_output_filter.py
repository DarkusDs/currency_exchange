from logger_setup import logger
from typing import List, Optional, Dict

def currency_output_filter(data: List[dict], valcode: Optional[str]) -> List[Dict]:
    """
    the function returns a list of dictionaries that satisfy the filtering condition by key, i.e. by currency name

    :param data:
    :param valcode:
    :param key_for_currency:
    :return:
    """
    if not valcode:
        return data
    else:
        filtered_data = []
        for row in data:
            if row.get("code", "") == valcode:
                filtered_data.append(row)
        logger.info(f"Виконано фільтурвання отриманого результату від API, для валюти: {valcode}")
        return filtered_data
