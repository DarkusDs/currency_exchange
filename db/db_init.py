import mysql.connector

from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST = getenv("DB_HOST")
DB_PORT = int(getenv("DB_PORT"))
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")

TABLES = {}

TABLES['exchange_rates'] = (
    """
    CREATE TABLE IF NOT EXISTS exchange_rates (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        bank VARCHAR(20) NOT NULL,
        currency VARCHAR(10) NOT NULL,
        name VARCHAR(100),
        rate DECIMAL(12,6) NOT NULL,
        rate_date DATE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        request_id CHAR(50),
        INDEX (request_id)
    )
    """
)
TABLES['users'] = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL,
    )
    """
)

def main():
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = cnx.cursor()
        cnx.database = DB_NAME

        for table_name, table_sql in TABLES.items():
            cursor.execute(table_sql)

        cursor.close()
        cnx.close()


    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

