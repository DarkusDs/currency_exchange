import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.api_logic import get_currency_exchange_rates
from utils.currency_output import format_currency_data
from utils.date_logic import validate_date
from utils.date_logic import get_validated_date

from db.crud import (
    create_exchange_rates,
    read_exchange_rates,
    update_exchange_rate,
    delete_exchange_rates
)

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


@app.get("/")
def home():
    """
    The function is responsible for displaying the default page

    :return:
    """
    return {"message": "Currency Exchange API", "docs": "/docs"}


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
        logger.error(f"в запиті {request_id} було передано банк, що не підтримується")
        raise HTTPException(status_code=400, detail="Банк має бути 'nbu' або 'privat'")

    raw_data = get_currency_exchange_rates(bank=bank, date=date_str, valcode=vcc)
    if not raw_data:
        logger.error(f"За запитом {request_id} не вдалося отримати курс валют")
        raise HTTPException(status_code=404, detail="Курси валют не знайдено")

    date_obj = datetime.strptime(date_str, "%Y%m%d")

    create_exchange_rates(
        bank=bank,
        rates_data=raw_data,
        rate_date=date_obj.date(),
        request_id=request_id
    )

    formatted_rates = format_currency_data(raw_data, date_obj, bank, vcc)

    rates_list = []

    for i in formatted_rates:
        found_code = None
        for item in raw_data:
            if item.get("name") == i.name:
                found_code = item.get("code")
                break

        currency_info = {
            "name": i.name,
            "code": found_code,
            "rate": i.rate,
            "date": i.date.strftime("%Y-%m-%d")
        }
        rates_list.append(currency_info)


    return {
        "request_id": request_id,
        "bank": bank,
        "date": date_str,
        "requested_currency": vcc or "всі",
        "rates": rates_list
    }


@app.get("/rates/db", response_model=List[RateResponse])
def get_rates_from_db(
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
            logger.error("Запит містив дату в неправильному форматі. Очікуваний формат: YYYYMMDD")
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
def create_manual_rate(rate: ManualRateCreate):
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
        logger.error("Не вдалося зберегти курс в базу даних")
        raise HTTPException(status_code=500, detail="Не вдалося зберегти курс")

    return {"message": "Курс успішно додано"}


@app.put("/rates/{rate_id}", response_model=dict)
def update_rate(rate_id: int, update_data: RateUpdate):
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
        logger.error("В запиті не було передано а ні rate а ні name, оновлення неможливе")
        raise HTTPException(status_code=400, detail="Для оновлення необхідно вказати rate або name або обидва")

    success = update_exchange_rate(
        rate_id=rate_id,
        new_rate=update_data.rate,
        new_name=update_data.name
    )

    if not success:
        logger.error("Не вдалося оновити курс")
        raise HTTPException(status_code=404, detail="Запис не знайдено або не оновлено")

    return {"message": "Курс успішно оновлено", "rate_id": rate_id}


@app.delete("/rates/{rate_id}", response_model=dict)
def delete_rate(rate_id: int):
    """
    function for manual delete existing rate in db
    example command in terminal:
    curl -X DELETE "http://localhost:8080/rates/157"

    :param rate_id:
    :return:
    """
    deleted = delete_exchange_rates(rate_id=rate_id)
    if deleted == 0:
        logger.error("Запиту з вказаним id не існує, помилка видалення")
        raise HTTPException(status_code=404, detail="Запис не знайдено")

    return {"message": "Курс успішно видалено", "deleted_id": rate_id, "count": deleted}
