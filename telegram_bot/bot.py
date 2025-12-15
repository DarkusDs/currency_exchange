import os
from datetime import datetime

import telebot
from dotenv import load_dotenv

from api.api_logic import get_currency_exchange_rates
from utils.currency_output import format_currency_data
from utils.date_logic import get_validated_date

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
                          "\n/help - короткий перелік всіх програм"
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
        date_object = datetime.strptime(date, "%Y%m%d")
        date_response = datetime.strftime(date_object, "%d-%m-%Y")
        raw_data = get_currency_exchange_rates(bank="nbu", date=date, valcode=vcc_param)
        if not raw_data:
            bot.send_message(chat_id, "Не вдалося отримати курси")
            return
        formated_data = format_currency_data(raw_data, date_object, 'nbu', vcc_param)
        response_nbu = f"Курс валют на {date_response}: \n---------------\n"
        for i in formated_data:
            rate = i.rate
            name = i.name

            code = ""
            for c in raw_data:
                if c.get("name") == i.name:
                    code = c.get('code')
                    break

            response_nbu += f"{code} - {name} - {rate} \n-----\n"
        bot.send_message(chat_id, response_nbu)
    except Exception as e:
        print(e)

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
        date_object = datetime.strptime(date, "%Y%m%d")
        date_response = datetime.strftime(date_object, "%d-%m-%Y")
        raw_data = get_currency_exchange_rates(bank="privat", date=date, valcode=vcc_param)
        if not raw_data:
            bot.send_message(chat_id, "Не вдалося отримати курси")
            return

        formated_data = format_currency_data(raw_data, date_object, 'privat', vcc_param)
        response_privat = f"Курс валют на {date_response}: \n---------------\n"
        for item in formated_data:
            code = item.name
            rate = item.rate
            name = CURRENCY_NAMES_PRIVAT.get(code)
            if rate is None:
                continue

            response_privat += f"{code} - {name} - {rate} \n-----\n"
        bot.send_message(chat_id, response_privat)
    except Exception as e:
        print(e)

bot.polling(none_stop=True, interval=0)
