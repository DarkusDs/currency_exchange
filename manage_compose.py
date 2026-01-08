import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

COMPOSE_FILE = "docker-compose.yml"

def generate_compose_file():
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    mysql_root_password = os.getenv("MYSQL_ROOT_PASSWORD")

    compose_template = f"""
services:
  app:
    build: .
    container_name: currency-app
    ports:
      - "8080:8000"
    depends_on:
      - db
    env_file:
      - .env
    environment:
      - DB_HOST={db_host}
      - DB_USER={db_user}
      - DB_PASSWORD={db_password}
      - DB_NAME={db_name}
    volumes:
      - ./logs:/app/logs

  db:
    image: mysql:8.0
    container_name: currency-mysql
    environment:
      MYSQL_ROOT_PASSWORD: {mysql_root_password}
      MYSQL_DATABASE: {db_name}
      MYSQL_USER: {db_user}
      MYSQL_PASSWORD: {db_password}
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: [ "CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "{db_user}", "--password={db_password}" ]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  bot:
    build: .
    container_name: currency-telegram-bot
    command: python -m telegram_bot.bot.py
    env_file:
      - .env
    environment:
      - DB_HOST={db_host}
      - DB_USER={db_user}
      - DB_PASSWORD={db_password}
      - DB_NAME={db_name}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    
  rabbitmq:
    image: rabbitmq:3-management
    container_name: currency-rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    
  worker:
    build: .
    container_name: currency-rabbitmq-worker
    command: python -m utils.rabbitmq start_worker
    env_file:
      - .env
    depends_on:
      - rabbitmq
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  mysql-data:
  rabbitmq-data:
"""

    with open(COMPOSE_FILE, "w", encoding="utf-8") as f:
        f.write(compose_template)
    print(f"Генеровано {COMPOSE_FILE}")

def start_compose():
    generate_compose_file()
    subprocess.run(["docker-compose", "-f", COMPOSE_FILE, "up", "-d", "--build"], check=True)
    print("Docker-compose піднято")

def stop_compose():
    subprocess.run(["docker-compose", "-f", COMPOSE_FILE, "down"], check=True)
    os.remove(COMPOSE_FILE)
    print("Docker-compose зупинено, файл видалено")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Використання: python manage_compose.py (start|stop)")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "start":
        start_compose()
    elif command == "stop":
        stop_compose()
    else:
        print("Невідома команда")
