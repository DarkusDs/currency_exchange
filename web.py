import os
import uuid

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Optional, List, Dict
import mysql.connector

from api_logic import get_currency_exchange_rates
from currency_output import format_currency_data, CurrencyRate
from date_logic import validate_date
from logger_setup import logger

app = FastAPI(
    title="Currency Exchange"
)

def get_valid_date(date_input: Optional[str]) -> str:
    if not date_input:
        return datetime.today().strftime("%Y%m%d")
    if not validate_date(date_input):
        raise HTTPException(status_code=400, detail="Неправильний формат дати. Очікується YYYYMMDD")
    return date_input


def save_rates_to_db(bank: str, rates_data: List[Dict], rate_date: datetime.date, request_id: str) -> int:
    if not rates_data:
        return 0

    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        cursor = conn.cursor()

        sql = """
            INSERT INTO exchange_rates 
            (bank, code, name, rate, rate_date, request_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = [
            (bank, item["code"], item["name"], float(item["rate"]), rate_date, request_id)
            for item in rates_data
            if item.get("code") and item.get("rate") is not None
        ]

        if not values:
            return 0

        cursor.executemany(sql, values)
        conn.commit()

    except Exception as e:
        logger.error(f"Помилка збереження в БД: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return 0

def format_response_rates(formatted_rates: List[CurrencyRate]) -> List[Dict]:
    return [
        {
            "name": r.name,
            "rate": r.rate,
            "date": r.date.strftime("%Y-%m-%d")
        }
        for r in formatted_rates
    ]

@app.get("/")
def home():
    return {"message": "Currency_exchange API"}

@app.get("/rates")
async def get_rates(
    bank: str ="nbu",
    date: Optional[str] = None,
    vcc: Optional[str] = None
):
    request_id = str(uuid.uuid4())
    date_str = get_valid_date(date)

    if bank not in ["nbu", "privat"]:
        raise HTTPException(status_code=400, detail="Банк має бути 'nbu' або 'privat'")

    raw_data = get_currency_exchange_rates(bank=bank, date=date_str, valcode=vcc)
    if not raw_data:
        raise HTTPException(status_code=404, detail="Курси валют не знайдено")

    date_obj = datetime.strptime(date_str, "%Y%m%d")
    formatted_rates = format_currency_data(raw_data, date_obj, bank, vcc)

    save_rates_to_db(
        bank=bank,
        rates_data=raw_data,
        rate_date=date_obj.date(),
        request_id=request_id
    )

    return {
        "request_id": request_id,
        "bank": bank,
        "date": date_str,
        "requested_currency": vcc or "всі",
        "rates": format_response_rates(formatted_rates)
    }


