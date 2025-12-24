import os
import uuid
from typing import List, Dict, Optional
import mysql.connector
from mysql.connector import Error
from datetime import date
import bcrypt


from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")

from db.connection import get_db_connection


def create_exchange_rates(bank: str, rates_data: List[Dict], rate_date: date, request_id: Optional[str] = None):
    """
    The function saves all received exchange rates from one bank for a specific date in a MySQL database, adding a unique query ID to each record

    :param bank:
    :param rates_data:
    :param rate_date:
    :param request_id:
    :return:
    """
    if not rates_data:
        return 0

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if not request_id:
            request_id = str(uuid.uuid4())

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

        cursor.executemany(sql, values)
        conn.commit()
        logger.info(
            f"Збережено курси (bank: {bank}, date: {rate_date}, request_id: {request_id or 'None'})")
        return True
    except Error as e:
        logger.error(f"Помилка створення записів у БД: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def read_exchange_rates(bank: Optional[str] = None, rate_date: Optional[date] = None, code: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    The function extracts the required exchange rates from the database (with filters by bank, date and currency code) and returns them as a list of dictionaries

    :param bank:
    :param rate_date:
    :param code:
    :param limit:
    :return:
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM exchange_rates WHERE 1=1"
        params = []


        if bank:
            sql += " AND bank = %s"
            params.append(bank)
        if rate_date:
            sql += " AND rate_date = %s"
            params.append(rate_date)
        if code:
            sql += " AND code = %s"
            params.append(code)

        sql += " ORDER BY rate_date DESC LIMIT %s"
        params.append(limit)

        cursor.execute(sql, params)
        results = cursor.fetchall()
        logger.info(f"Успішно прочитано {len(results)} записів з БД")
        return results

    except Error as e:
        logger.error(f"Помилка читання з БД: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_exchange_rate(rate_id: Optional[int] = None, bank: Optional[str] = None, code: Optional[str] = None, rate_date: Optional[date] = None, new_rate: float = None, new_name: Optional[str] = None) -> bool:
    """
    The function updates the rate or currency name in the database either by id or by a unique combination of bank + code + rate_date

    :param rate_id:
    :param bank:
    :param code:
    :param rate_date:
    :param new_rate:
    :param new_name:
    :return:
    """
    if not (rate_id or (bank and code and rate_date)):
        logger.error("Для оновлення потрібен ID або комбінація bank + code + rate_date")
        return False

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "UPDATE exchange_rates SET"
        params = []
        updates = []

        if new_rate is not None:
            updates.append(" rate = %s")
            params.append(new_rate)
        if new_name:
            updates.append(" name = %s")
            params.append(new_name)

        if not updates:
            logger.warning("Немає даних для оновлення")
            return False

        sql += ",".join(updates) + " WHERE 1=1"

        if rate_id:
            sql += " AND id = %s"
            params.append(rate_id)
        else:
            sql += " AND bank = %s AND code = %s AND rate_date = %s"
            params.extend([bank, code, rate_date])

        cursor.execute(sql, params)
        conn.commit()
        updated = cursor.rowcount > 0
        if updated:
            logger.info(f"Успішно оновлено запис (ID: {rate_id or 'по фільтру'})")
        return updated

    except Error as e:
        logger.error(f"Помилка оновлення в БД: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_exchange_rates(rate_id: Optional[int] = None, bank: Optional[str] = None, rate_date: Optional[date] = None, code: Optional[str] = None):
    """
    The function deletes one or many records from the database using any combination of filters (id, bank, date, code)

    :param rate_id:
    :param bank:
    :param rate_date:
    :param code:
    :return:
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM exchange_rates WHERE 1=1"
        params = []

        if rate_id:
            sql += " AND id = %s"
            params.append(rate_id)
        if bank:
            sql += " AND bank = %s"
            params.append(bank)
        if rate_date:
            sql += " AND rate_date = %s"
            params.append(rate_date)
        if code:
            sql += " AND code = %s"
            params.append(code)

        cursor.execute(sql, params)
        conn.commit()
        deleted_count = cursor.rowcount
        logger.info(f"Успішно видалено {deleted_count} записів з БД")
        return deleted_count

    except Error as e:
        logger.error(f"Помилка видалення з БД: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(username: str, hashed_password: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO users (username, hashed_password) VALUES (%s, %s)"
        cursor.execute(sql, (username, hashed_password))
        conn.commit()

        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating user in DB: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_user_by_username(username: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user:
            return user
        else:
            return None
    except Exception as e:
        raise Exception(f"Користувач відсутній в базі: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

