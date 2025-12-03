import mysql.connector
import pyodbc
import os


def connect():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "currency_user"),
            password=os.getenv("DB_PASSWORD", "12345678"),
            database=os.getenv("DB_NAME", "currency_db")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exchange_rates")

        cursor.execute("SELECT bank, code, rate, rate_date FROM exchange_rates LIMIT 5")
        for row in cursor.fetchall():
            print(row)

        cursor.close()
        conn.close()
    except Exception as e:
        print("Помилка підключення:", e)
