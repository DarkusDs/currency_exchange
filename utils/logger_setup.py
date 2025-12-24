import logging
import uuid
import os

log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)

base_logger = logging.getLogger("currency_app")
base_logger.setLevel(logging.INFO)
base_logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(source)s - %(unic_id)s - %(message)s"
)

file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

base_logger.handlers.clear()
base_logger.addHandler(file_handler)

def get_logger(source: str = "SYSTEM"):
    request_id = str(uuid.uuid4())
    extra = {
        "source": source.upper(),
        "unic_id": request_id
    }
    return logging.LoggerAdapter(base_logger, extra)
