import uuid
from datetime import datetime
from uuid import uuid4

from celery import Celery
from celery.schedules import crontab

from utils.date_logic import get_validated_date
from utils.rabbitmq import PublisherRPCRabbitMQ
from utils.settings import QUEUE_REQUEST_NAME

app = Celery("currency_scheduler", broker='amqp://guest:guest@rabbitmq:5672//')


from utils.logger_setup import get_logger

logger = get_logger("SCHEDULER")
logger.info(f"Scheduler initialized")

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):


    # Executes every 5 minutes
    sender.add_periodic_task(
        crontab(minute='*/10'),
        refresh_rates.s(),
    )

@app.task(name="refresh_rates")
def refresh_rates():


    rpc = PublisherRPCRabbitMQ()
    today = datetime.today().strftime('%Y%m%d')
    for bank in ('nbu', 'privat'):
        request_id = f"AUTO_{uuid.uuid4().hex[:8]}"
        request = {
            "task_type": "get_rates",
            "bank": bank,
            "date": today,
            "valcode": None,
            "request_id": request_id,
        }
        logger.info(f"sending [Auto] request to bank: {bank}")

        response = rpc.call(
            routing_key=QUEUE_REQUEST_NAME,
            request_body=request,
            timeout=20.0,
        )
        if response is None:
            logger.error(f"RPC timeout - [Auto] - for bank {bank}")
            continue

        if not isinstance(response, dict):
            logger.error(f"Invalid RPC response - [Auto] - for bank {bank}")
            continue

        if response.get('status') != "success":
            logger.error(f"worker return error - [Auto] - for bank {bank}")
            continue

        logger.info(f"Complete Auto request to bank: {bank}")

