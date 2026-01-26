import uuid

from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from utils.date_logic import validate_date
from utils.date_logic import get_validated_date

from utils.rabbitmq import PublisherRPCRabbitMQ
from utils.settings import QUEUE_REQUEST_NAME

from db.crud import (
    create_exchange_rates,
    read_exchange_rates,
    update_exchange_rate,
    delete_exchange_rates, get_user_by_username, verify_password
)

from api.auth import get_current_user

from db.crud import create_user
from db.crud import hash_password


from utils.logger_setup import get_logger
logger = get_logger("WEB")

app = FastAPI(
    title="Currency Exchange"
)

class ManualRateCreate(BaseModel):
    """
    Pydantic model, which requires specific fields from the user when adding courses manually
    """
    bank: str
    code: str
    name: str
    rate: float
    rate_date: str


class RateUpdate(BaseModel):
    """
    Pydantic model that allows you to optionally change the rate or name
    """
    rate: Optional[float] = None
    name: Optional[str] = None


class RateResponse(BaseModel):
    """
    Pydantic model, which is responsible for the form in which the data will be returned
    """
    id: int
    bank: str
    code: str
    name: str
    rate: float
    rate_date: str
    request_id: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    """
    The function is responsible for displaying the default page

    :return:
    """
    return {"message": "Currency Exchange API", "docs": "/docs"}


@app.post("/register")
def register(user: RegisterRequest):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)

    create_user(user.username, hashed_password)

    return {"message": "User registered successfully"}

from fastapi.security import OAuth2PasswordRequestForm
from api.auth import create_access_token, Token, authenticate_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/rates", response_model=dict)
def get_rates_from_api(
    bank: str = "nbu",
    date: Optional[str] = None,
    vcc: Optional[str] = None
):
    """
    the function return the requested currency rates

    :param bank: 'nbu' or 'privat', default: 'nbu'
    :param date:
    :param vcc:
    :return:
    """
    request_id = str(uuid.uuid4().hex[:8])
    date_str = get_validated_date(date)

    if bank not in ["nbu", "privat"]:
        logger.error(f"The request {request_id} contained an unsupported bank")
        raise HTTPException(status_code=400, detail="Банк має бути 'nbu' або 'privat'")

    rpc = PublisherRPCRabbitMQ()

    request = {
        "task_type": "get_rates",
        "bank": bank,
        "date": date_str,
        "valcode": vcc,
        "request_id": f"WEB_{request_id}",
    }

    response = rpc.call(
        routing_key=QUEUE_REQUEST_NAME,
        request_body=request,
        timeout=20.0
    )

    if response is None:
        logger.error(f"Timeout error or worker unavailability. request_id={request_id}")
        raise HTTPException(status_code=504, detail="RPC timeout")

    if not isinstance(response, dict):
        logger.error(f"Incorrect response from the worker {response}")
        raise HTTPException(status_code=502, detail="Некоректна відповідь воркера")

    if response.get("status") != "success":
        logger.error(f"Worker returned a request processing error")



    result = {
        "request_id": request_id,
        "bank": bank,
        "date": date_str,
        "requested_currency": vcc or "всі",
        "text": response.get("text", "")
    }

    if "rates" in response:
        result["rates"] = response["rates"]
    else:
        result["rates"] = []

    return result


@app.get("/rates/db", response_model=List[RateResponse])
def get_rates_from_db(
    current_user: str = Depends(get_current_user),
    bank: Optional[str] = None,
    date: Optional[str] = None,
    code: Optional[str] = None,
    limit: int = 50
):
    """
    function return a number of remaining records from the database, depending on the input of search parameters

    :param bank:
    :param date:
    :param code:
    :param limit: limit for results count, default: 50
    :return:
    """
    rate_date_obj = None
    if date:
        if not validate_date(date):
            logger.error("The request contained a date in the wrong format. Expected format: YYYYMMDD")
            raise HTTPException(status_code=400, detail="Невірний формат дати")
        rate_date_obj = datetime.strptime(date, "%Y%m%d").date()

    rates = read_exchange_rates(
        bank=bank,
        rate_date=rate_date_obj,
        code=code,
        limit=limit
    )

    result_list = []

    for i in rates:
        one_rate = RateResponse(
            id=i["id"],
            bank=i["bank"],
            code=i["code"],
            name=i["name"],
            rate=float(i["rate"]),
            rate_date=i["rate_date"].strftime("%Y%m%d"),
            request_id=i["request_id"]
        )
        result_list.append(one_rate)
    return result_list


@app.post("/rates/manual", response_model=dict)
def create_manual_rate(rate: ManualRateCreate, current_user: str = Depends(get_current_user)):
    """
    function for manual adding new rate in db
    example command in terminal:
    curl -X POST "http://localhost:8080/rates/manual" \
     -H "Content-Type: application/json" \
     -d '{
           "bank": "name of bank",
           "code": "currency code",
           "name": "currency name",
           "rate": currency rate,
           "rate_date": "date for rate"
         }'

    :param rate:
    :return:
    """
    date_obj = datetime.strptime(rate.rate_date, "%Y%m%d").date()

    inserted = create_exchange_rates(
        bank=rate.bank,
        rates_data=[{
            "code": rate.code,
            "name": rate.name,
            "rate": rate.rate
        }],
        rate_date=date_obj
    )

    if inserted == 0:
        logger.error("Failed to save the course to the database")
        raise HTTPException(status_code=500, detail="Не вдалося зберегти курс")

    return {"message": "Курс успішно додано"}


@app.put("/rates/{rate_id}", response_model=dict)
def update_rate(rate_id: int, update_data: RateUpdate, current_user: str = Depends(get_current_user)):
    """
    function for manual update existing rate in db
    example command in terminal:
    curl -X PUT "http://localhost:8080/rates/157" \
     -H "Content-Type: application/json" \
     -d '{"rate": 42.50}'

    :param rate_id:
    :param update_data:
    :return:
    """
    if not update_data.rate and not update_data.name:
        logger.error("Neither rate nor name was transmitted in the request; update is not possible")
        raise HTTPException(status_code=400, detail="Для оновлення необхідно вказати rate або name або обидва")

    success = update_exchange_rate(
        rate_id=rate_id,
        new_rate=update_data.rate,
        new_name=update_data.name
    )

    if not success:
        logger.error("Failed to update the exchange rate")
        raise HTTPException(status_code=404, detail="Запис не знайдено або не оновлено")

    return {"message": "Курс успішно оновлено", "rate_id": rate_id}


@app.delete("/rates/{rate_id}", response_model=dict)
def delete_rate(rate_id: int, current_user: str = Depends(get_current_user)):
    """
    function for manual delete existing rate in db
    example command in terminal:
    curl -X DELETE "http://localhost:8080/rates/157"

    :param rate_id:
    :return:
    """
    deleted = delete_exchange_rates(rate_id=rate_id)
    if deleted == 0:
        logger.error("The query with the specified ID does not exist, deletion error")
        raise HTTPException(status_code=404, detail="Запис не знайдено")

    return {"message": "Курс успішно видалено", "deleted_id": rate_id, "count": deleted}





