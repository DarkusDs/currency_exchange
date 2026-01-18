import os
from datetime import datetime

import pika
import telebot
from dotenv import load_dotenv

from utils.currency_output import format_currency_data
from utils.date_logic import get_validated_date

from uuid import uuid4

from utils.rabbitmq import PublisherRPCRabbitMQ

rpc_client = PublisherRPCRabbitMQ()

from utils.logger_setup import get_logger
logger = get_logger("BOT")

CURRENCY_NAMES_PRIVAT = {
    "USD": "Долар США",
    "EUR": "Євро",
    "GBP": "Фунт стерлінгів",
    "CHF": "Швейцарський франк",
    "PLN": "Злотий",
    "CZK": "Чеська крона",
}

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, "Привіт, ви звернулися до боту який вміє показувати курси валют \nВідправте команду /help щоб побачити весь наший можливий функціонал")

@bot.message_handler(commands=['help'])
def send_help(message: telebot.types.Message):
    bot.reply_to(message, "Наші команди: \n"
                          "\n/help - короткий перелік всіх команд"
                          "\n/nbu - вивід курсу всіх валют на цей день від НБУ, через пробіл можна по бажанню додати як параметри код валюти та дату в форматі YYYYMMDD, розділяючи пробілом"
                          "\n/privat - вивід курсу всіх валют на цей день від ПриватБанку, через пробіл можна по бажанню додати як параметри код валюти та дату в форматі YYYYMMDD, розділяючи пробілом")

@bot.message_handler(commands=['nbu'])
def send_nbu_rates(message: telebot.types.Message):
    chat_id = message.chat.id
    command_params = message.text.strip().split()

    vcc_param = None
    date_param = None

    for p in command_params[1:]:
        if len(p) == 8:
            date_param = p
        elif len(p) == 3:
            vcc_param = p
        else:
            bot.send_message(chat_id, "Невірна форма вводу")

    try:
        date = get_validated_date(date_param)
        request_id = f"BOT_{uuid4().hex[:8]}"
        request = {
            "task_type": "get_rates",
            "bank": "nbu",
            "date": date,
            "valcode": vcc_param,
            "request_id": request_id
        }

        response = rpc_client.call(
            routing_key="currency_requests",
            request_body=request,
            timeout=20.0
        )

        if response and isinstance(response, dict) and response.get("status") == "success":
            bot.send_message(chat_id, response["text"])
        else:
            error_msg = response.get("error", "Не вдалося отримати курси") if isinstance(response, dict) else "помилка"
            bot.send_message(chat_id, error_msg)

    except Exception as e:
        logger.exception(f"ПОМИЛКА в /nbu: {str(e)}")
        bot.send_message(chat_id, f"Щось пішло не так: {str(e)}")

@bot.message_handler(commands=['privat'])
def send_privat_rates(message: telebot.types.Message):
    chat_id = message.chat.id
    command_params = message.text.strip().split()

    vcc_param = None
    date_param = None

    for p in command_params[1:]:
        if len(p) == 8:
            date_param = p
        elif len(p) == 3:
            vcc_param = p
        else:
            bot.send_message(chat_id, "Невірна форма вводу")

    try:
        date = get_validated_date(date_param)
        request_id = f"BOT_{uuid4().hex[:8]}"
        request = {
            "task_type": "get_rates",
            "bank": "privat",
            "date": date,
            "valcode": vcc_param,
            "request_id": request_id
        }

        response = rpc_client.call(
            routing_key="currency_requests",
            request_body=request,
            timeout=20.0
        )

        if response and isinstance(response, dict) and response.get("status") == "success":
            bot.send_message(chat_id, response["text"])
        else:
            error_msg = response.get("error", "Не вдалося отримати курси") if isinstance(response, dict) else "помилка"
            bot.send_message(chat_id, error_msg)

    except Exception as e:
        logger.exception(f"ПОМИЛКА в /nbu: {str(e)}")
        bot.send_message(chat_id, f"Щось пішло не так: {str(e)}")


bot.polling(none_stop=True, interval=0)
