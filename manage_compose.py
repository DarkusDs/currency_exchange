import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

COMPOSE_FILE = "docker-compose.yml"


def generate_compose_file():
    """
    Generates a docker-compose.yml file dynamically using environment variables

    :return:
    """
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    mysql_root_password = os.getenv("MYSQL_ROOT_PASSWORD")
    redis_host = os.getenv("REDIS_HOST")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_port = os.getenv("REDIS_PORT")
    redis_databases = os.getenv("REDIS_DATABASES")

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
      - .:/app
    command: >
      sh -c "uvicorn web:app --host 0.0.0.0 --port 8000"

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
      rabbitmq:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - .:/app

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
    healthcheck:
      test: ["CMD", "rabbitmqctl", "status"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
      
  scheduler:
    build: .
    container_name: currency_scheduler
    command: celery -A utils.scheduler:app worker -B -l info
    depends_on:
      rabbitmq:
        condition: service_healthy
    env_file:
      - .env
    volumes:
      - .:/app
      - .:/logs:/app/logs
    restart: unless-stopped

  request_worker:
    build: .
    container_name: currency-request-worker
    command: python -m workers.request_processor
    env_file:
      - .env
    depends_on:
      rabbitmq:
        condition: service_healthy
    volumes:
      - .:/app
    restart: unless-stopped

  save_worker:
    build: .
    container_name: currency-save-worker
    command: python -m workers.save_worker
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    volumes:
      - .:/app
      - ./logs:/app/logs
    restart: unless-stopped
      
  redis:
    image: redis:alpine
    container_name: currency-redis
    restart: always
    ports:
      - "6379:6379"
    env_file:
      - .env
    environment:
      - REDIS_HOST={redis_host}
      - REDIS_PASSWORD={redis_password}
      - REDIS_DATABASES={redis_databases}
      - REDIS_PORT={redis_port}
    volumes:
      - redis-data:/data

volumes:
  mysql-data:
  rabbitmq-data:
  redis-data:
"""

    with open(COMPOSE_FILE, "w", encoding="utf-8") as f:
        f.write(compose_template)
    print(f"Генеровано {COMPOSE_FILE}")

def up_compose():
    """
    Generates the compose file and starts all services in detached mode

    :return:
    """
    generate_compose_file()
    subprocess.run(
        ["docker-compose", "-f", COMPOSE_FILE, "up", "-d"],
        check=True
    )
    print("Docker-compose успішно піднято")

def build_compose():
    """
    Builds Docker images for all services defined in the compose file

    :return:
    """
    generate_compose_file()
    subprocess.run(
        ["docker-compose", "-f", COMPOSE_FILE, "build"],
        check=True
    )
    print("Docker успішно перебілджено")

def start_compose():
    """
    Starts previously created containers without rebuilding them

    :return:
    """
    subprocess.run(
        ["docker-compose", "-f", COMPOSE_FILE, "start"],
        check=True
    )
    print("Docker-compose успішно запущено")

def stop_compose():
    """
    Stops running containers without removing them

    :return:
    """
    subprocess.run(
        ["docker-compose", "-f", COMPOSE_FILE, "stop"],
        check=True
    )
    print("Docker-compose успішно зупинено")

def down_compose():
    """
    Stops and removes all containers, networks, and the generated compose file

    :return:
    """
    subprocess.run(
        ["docker-compose", "-f", COMPOSE_FILE, "down"],
        check=True
    )
    if os.path.exists(COMPOSE_FILE):
        os.remove(COMPOSE_FILE)

    print("Docker-compose успішно зупинено і файл видалено")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python manage_compose.py (up/build/start/stop/down)")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "up":
        up_compose()
    elif command == "build":
        build_compose()
    elif command == "start":
        start_compose()
    elif command == "stop":
        stop_compose()
    elif command == "down":
        down_compose()
    else:
        print("Невідома команда")


