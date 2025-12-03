from typing import Optional, Dict
import requests
from requests.exceptions import HTTPError
from logger_setup import logger
from requests import URLRequired


def _send_get_request(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    res = None
    try:
        res = requests.get(url, params=params)
        res = res.json()
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
