from utils.parser import parse_arguments
from utils.rabbitmq import PublisherRPCRabbitMQ
from utils.settings import QUEUE_REQUEST_NAME
from uuid import uuid4

from utils.logger_setup import get_logger
logger = get_logger("CLI")

def main():
    """
    Parses CLI arguments, sends an RPC request for currency rates, and displays the response in a human-readable format

    :return:
    """
    args = parse_arguments()
    bank = args.bank
    date = args.currency_date
    vcc = args.vcc.upper() if args.vcc else None
    request_id = f"CLI_{uuid4().hex[:8]}"

    request = {
        "task_type": "get_rates",
        "bank": bank,
        "date": date,
        "valcode": vcc,
        "request_id": request_id
    }

    rpc = PublisherRPCRabbitMQ()
    response = rpc.call(
        routing_key=QUEUE_REQUEST_NAME,
        request_body=request,
        timeout=20.0,
    )

    if response is None:
        logger.error(f"Timeout: {request_id}")
        return

    if not isinstance(response, dict):
        logger.error(f"Incorrect response to the worker: {response}")
        return

    if response.get("status") != "success":
        logger.error("Request processing error")
        return

    text = response.get("text", "")
    if text:
        print(text)
        return

    rates = response.get("rates", [])
    if not rates:
        print("Даних немає")
        return

    for rate in rates:
        print(f"{rate.get('code')} - {rate.get('name')} - {rate.get('rate')} - {rate.get('date')}")

if __name__ == '__main__':
    main()

