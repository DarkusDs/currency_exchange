from db.connection import get_db_connection


def connect():
    """
    Establishes a test connection to the database and prints a small sample of exchange rate records
    """
    try:
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM exchange_rates")

        cursor.execute("SELECT bank, code, rate, rate_date FROM exchange_rates LIMIT 5")
        for row in cursor.fetchall():
            print(row)

        cursor.close()
        get_db_connection().close()
    except Exception as e:
        print("Помилка підключення:", e)
