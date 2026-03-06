from typing import Optional, Dict
import requests
from requests.exceptions import HTTPError
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")
from requests import URLRequired


def _send_get_request(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Sends an HTTP GET request to the specified URL and returns the parsed JSON response.
    Logs request-related errors and returns None if the request fails

    :param url: Target URL for the HTTP GET request
    :param params: Optional query parameters to be sent with the request
    :return: Parsed JSON response as a dictionary, or None if an error occurs
    """
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
#
# import httpx
# logger = get_logger("ASYNC_SENDER")
#
# async def _send_get_request(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
#     """
#     Asynchronously sends an HTTP GET request to the specified URL with optional parameters
#     and returns the parsed JSON response.
#
#     :param url: Target URL for the HTTP GET request
#     :param params: Optional query parameters to be sent with the request
#     :return: Parsed JSON response as a dictionary, or None if an error occurs
#     """
#     res = None
#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.get(url, params=params)
#             response.raise_for_status()
#             return response.json()
#     except HTTPError as e:
#         logger.error("HTTP Error")
#     except ConnectionError as e:
#         logger.error("ConnectionError")
#     except URLRequired as e:
#         logger.error("URLRequired")
#     except Exception as e:
#         logger.error(e)
#     finally:
#         return res

