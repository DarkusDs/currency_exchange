import mysql.connector
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST = getenv("DB_HOST")
DB_PORT = int(getenv("DB_PORT", "3306"))
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")

TABLES = {
    "exchange_rates": """
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            bank VARCHAR(10) NOT NULL,
            code VARCHAR(10) NOT NULL,
            name VARCHAR(100),
            rate DECIMAL(12,6) NOT NULL,
            rate_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            request_id CHAR(36),
            INDEX (request_id)
        )
    """,
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL
        )
    """
}

def main():
    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = cnx.cursor()

        for table_name, table_sql in TABLES.items():
            cursor.execute(table_sql)

        cnx.commit()

    except Exception as e:
        raise
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

if __name__ == "__main__":
    main()
