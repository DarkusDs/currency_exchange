import uuid
from typing import List, Dict, Optional
from mysql.connector import Error
from datetime import date
import bcrypt

from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")

from db.connection import get_db_connection


def create_exchange_rates(bank: str, rates_data: List[Dict], rate_date: date, request_id: Optional[str] = None):
    """
    Saves a batch of exchange rates for a specific bank and date into the database, assigning a unique request identifier to all records

    :param bank: Bank identifier (e.g. "nbu", "privat")
    :param rates_data: List of unified currency rate dictionaries to be stored
    :param rate_date: Date for which the exchange rates apply
    :param request_id: Optional request identifier; generated automatically if not provided
    :return: True if records were inserted successfully, or 0 if no data was provided
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
            f"Saved rates (bank: {bank}, date: {rate_date}, request_id: {request_id or 'None'})")
        return True
    except Error as e:
        logger.error(f"Error creating records in the database: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def read_exchange_rates(bank: Optional[str] = None, rate_date: Optional[date] = None, code: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    Retrieves exchange rate records from the database using optional filtering and result limiting

    :param bank: Optional bank identifier to filter results
    :param rate_date: Optional date to filter exchange rates
    :param code: Optional currency code to filter results
    :param limit: Maximum number of records to return
    :return: A list of exchange rate records represented as dictionaries
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
        logger.info(f"Successfully read {len(results)} records from the database")
        return results

    except Error as e:
        logger.error(f"Error reading from database: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_exchange_rate(rate_id: Optional[int] = None, bank: Optional[str] = None, code: Optional[str] = None, rate_date: Optional[date] = None, new_rate: float = None, new_name: Optional[str] = None) -> bool:
    """
    Updates an existing exchange rate record identified by ID or by bank, currency code, and date

    :param rate_id: Optional unique identifier of the exchange rate record
    :param bank: Bank identifier used for composite lookup
    :param code: Currency code used for composite lookup
    :param rate_date: Date used for composite lookup
    :param new_rate: New exchange rate value to be set
    :param new_name: New currency name to be set
    :return: True if the record was updated successfully, otherwise False
    """
    if not (rate_id or (bank and code and rate_date)):
        logger.error("To update, you need an ID or a combination of bank + code + rate_date")
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
            logger.warning("No data available for update")
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
            logger.info(f"Record successfully updated (ID: {rate_id or 'by filter'})")
        return updated

    except Error as e:
        logger.error(f"Database update error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_exchange_rates(rate_id: Optional[int] = None, bank: Optional[str] = None, rate_date: Optional[date] = None, code: Optional[str] = None):
    """
    Deletes one or more exchange rate records from the database using flexible filter criteria

    :param rate_id: Optional unique identifier of the exchange rate record
    :param bank: Optional bank identifier to filter records
    :param rate_date: Optional date to filter records
    :param code: Optional currency code to filter records
    :return: Number of deleted records
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
        logger.info(f"{deleted_count} records successfully deleted from the database")
        return deleted_count

    except Error as e:
        logger.error(f"Error deleting from database: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(username: str, hashed_password: str):
    """
    Creates a new user record in the database with a pre-hashed password

    :param username: Username of the new user
    :param hashed_password: Securely hashed user password
    :return: Identifier of the newly created user record
    """
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
    """
    Retrieves a user record from the database by username

    :param username: Username to search for
    :return: User record as a dictionary, or None if the user does not exist
    """
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
    """
    Generates a secure bcrypt hash from a plain-text password

    :param password: Plain-text password provided by the user
    :return: Hashed password string suitable for database storage
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash

    :param plain_password: Plain-text password provided by the user
    :param hashed_password: Stored bcrypt-hashed password
    :return: True if the password matches the hash, otherwise False
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

