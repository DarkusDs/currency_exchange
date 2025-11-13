import logging
import uuid

req_id = {'unic_id': str(uuid.uuid4())}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(unic_id)s - %(message)s")
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger = logging.LoggerAdapter(logger, req_id)
