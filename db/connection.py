import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from utils.logger_setup import get_logger
logger = get_logger("SYSTEM")

load_dotenv()
def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database using environment variables.
    Logs connection errors and raises an exception if the connection cannot be created

    :return: An active MySQL database connection object
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except Error as e:
        logger.error(f"Error connecting to the database: {e}")
        raise
