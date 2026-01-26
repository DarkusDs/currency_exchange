import os
import telebot
from dotenv import load_dotenv
from utils.date_logic import get_validated_date
from uuid import uuid4
from utils.rabbitmq import PublisherRPCRabbitMQ
rpc_client = PublisherRPCRabbitMQ()
from utils.logger_setup import get_logger
logger = get_logger("BOT")
from api.auth import verify_access_token
from utils.settings import REDIS_CLIENT

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

TOKEN_TTL_SECONDS = 60 * 60 * 24
def token_key(chat_id: int) -> str:
    """
    Builds a Redis key used to store a JWT token bound to a specific Telegram chat

    :param chat_id: Telegram chat identifier used to scope the stored token
    :return: Redis key string in the format "tg:token:<chat_id>"
    """
    return f"tg:token:{chat_id}"

def save_token(chat_id: int, token: str) -> None:
    """
    Stores a JWT token in Redis for the given chat ID with a predefined TTL

    :param chat_id: Telegram chat identifier to bind the token to
    :param token: JWT access token string to store
    """
    REDIS_CLIENT.client.setex(token_key(chat_id), TOKEN_TTL_SECONDS, token)

def get_token(chat_id: int) -> str:
    """
    Retrieves the stored JWT token for a chat from Redis (if present)

    :param chat_id: Telegram chat identifier associated with the token
    :return: JWT token string if found, otherwise None (Redis returns None when key is missing)
    """
    return REDIS_CLIENT.client.get(token_key(chat_id))

def delete_token(chat_id: int) -> None:
    """
    Removes the stored JWT token for the given chat ID from Redis

    :param chat_id: Telegram chat identifier whose token should be deleted
    :return: None
    """
    REDIS_CLIENT.client.delete(token_key(chat_id))

@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    """
    Sends a welcome message describing the bot purpose and how to access the command list

    :param message: Telegram message object that triggered the command
    :return: None
    """
    bot.reply_to(message, "Привіт, ви звернулися до боту який вміє показувати курси валют \nВідправте команду /help щоб побачити весь наший можливий функціонал")

@bot.message_handler(commands=['help'])
def send_help(message: telebot.types.Message):
    """
    Sends a help message listing available bot commands and their usage

    :param message: Telegram message object that triggered the command
    :return: None
    """
    bot.reply_to(message, "Наші команди: \n"
                          "\n/help - короткий перелік всіх команд"
                          "\n/link - після команди введіть через пробіл токен отриманий через /login в веб версії додатку. Таким чином ви прив'яжете токен до чату і зможете користуватися захищеними командами"
                          "\n/unlink - для примусової відв'язки токену"
                          "\n/nbu - вивід курсу всіх валют на цей день від НБУ, через пробіл можна по бажанню додати як параметри код валюти та дату в форматі YYYYMMDD, розділяючи пробілом"
                          "\n/privat - вивід курсу всіх валют на цей день від ПриватБанку, через пробіл можна по бажанню додати як параметри код валюти та дату в форматі YYYYMMDD, розділяючи пробілом")

@bot.message_handler(commands=['nbu'])
def send_nbu_rates(message: telebot.types.Message):
    """
    Requests NBU exchange rates via RPC and replies with formatted results, requiring a linked JWT token

    :param message: Telegram message object containing command arguments (date/currency code)
    :return: None
    """
    chat_id = message.chat.id
    token = get_token(chat_id)
    if not token:
        bot.send_message(chat_id, "Підвяжіть токен")
        return

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
            error_msg = response.get("Не вдалося отримати курси") if isinstance(response, dict) else "помилка"
            bot.send_message(chat_id, error_msg)

    except Exception as e:
        logger.exception(f"Error at /nbu: {str(e)}")
        bot.send_message(chat_id, f"Something wrong: {str(e)}")

@bot.message_handler(commands=['privat'])
def send_privat_rates(message: telebot.types.Message):
    """
    Requests PrivatBank exchange rates via RPC and replies with formatted results, requiring a linked JWT token

    :param message: Telegram message object containing command arguments (date/currency code)
    :return: None
    """
    chat_id = message.chat.id
    token = get_token(chat_id)
    if not token:
        bot.send_message(chat_id, "Підвяжіть токен")
        return
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
            error_msg = response.get("Не вдалося отримати курси") if isinstance(response, dict) else "помилка"
            bot.send_message(chat_id, error_msg)

    except Exception as e:
        logger.exception(f"Error at /nbu: {str(e)}")
        bot.send_message(chat_id, f"Something wrong: {str(e)}")

@bot.message_handler(commands=['link'])
def link_account(message: telebot.types.Message):
    """
    Validates a provided JWT token and stores it in Redis to link the current chat with a user session

    :param message: Telegram message object containing the token after the /link command
    :return: None
    """
    chat_id = message.chat.id
    parts = message.text.strip().split(maxsplit=1)
    token = parts[1].strip()
    try:
        payload = verify_access_token(token)
        username = payload.get("sub")
        if not username:
            bot.send_message(chat_id, "В токені не передано інформації про користувача, спробуйте залогінитися ще раз")
            return
        save_token(chat_id, token)
        bot.send_message(chat_id, "Акаунт підвязано")
    except Exception as e:
        bot.send_message(chat_id, "Токен недійсний")

@bot.message_handler(commands=['unlink'])
def unlink_account(message: telebot.types.Message):
    """
    Unlinks the chat from authentication by deleting the stored JWT token from Redis

    :param message: Telegram message object that triggered the command
    :return: None
    """
    chat_id = message.chat.id
    delete_token(chat_id)
    bot.send_message(chat_id, "Токен видалено, акаунт відвязано")

bot.polling(none_stop=True, interval=0)
