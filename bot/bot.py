import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telebot import TeleBot, types
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

# Получаем токен бота из переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print("Ошибка: переменная окружения TELEGRAM_BOT_TOKEN не установлена.")
    exit(1)

bot = TeleBot(TOKEN)

# Настройка логирования
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/telegram_bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
logger = logging.getLogger(__name__)

# Получаем URL приложения из переменной окружения
APP_URL = os.getenv('APP_URL', 'https://projecteos.xyz')

print("Bot is starting...")
logger.info("Bot is starting...")

# Инициализируем базу данных SQLite
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, launches_left INTEGER, payment_expiry TEXT)''')
conn.commit()

# Стоимость и номер счёта для оплаты
PAYMENT_AMOUNT = 0.2  # Стоимость в TONCOIN
TON_WALLET = 'ВАШ_НОМЕР_СЧЁТА_TON'  # Замените на ваш номер счёта

# Функция для отправки ссылки на веб-приложение
def send_app_link(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app_button = KeyboardButton(text="Открыть Web App", web_app=WebAppInfo(url=APP_URL))
    keyboard.add(web_app_button)
    keyboard.add(KeyboardButton("Support"))
    bot.send_message(chat_id, "Нажмите кнопку ниже, чтобы открыть приложение:", reply_markup=keyboard)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    send_app_link(message.chat.id)
    logger.info(f'Sent welcome message with Web App to user {message.chat.id}')
    print(f"Sent welcome message to user {message.chat.id}")

    # Добавляем пользователя в базу данных, если его там нет
    cursor.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    user_data = cursor.fetchone()
    if not user_data:
        cursor.execute("INSERT INTO users (user_id, launches_left, payment_expiry) VALUES (?, ?, ?)",
                       (message.chat.id, 2, None))
        conn.commit()

# Обработчик нажатий кнопок
@bot.message_handler(func=lambda message: True)
def on_click(message):
    text = message.text
    if text == 'Support':
        message_text = f"Чтобы продолжить использование приложения после 2 бесплатных запусков, пожалуйста, сделайте платеж в размере {PAYMENT_AMOUNT} TON на кошелек {TON_WALLET}."
        bot.send_message(message.chat.id, message_text)
        logger.info(f'Sent support message to user {message.chat.id}')
        print(f"Sent support message to user {message.chat.id}")
        
    elif text == 'Открыть Web App':
        cursor.execute("SELECT launches_left, payment_expiry FROM users WHERE user_id=?", (message.chat.id,))
        user_data = cursor.fetchone()
        if user_data:
            launches_left, payment_expiry = user_data
            if payment_expiry:
                # Проверяем, активен ли оплаченный период
                expiry_date = datetime.strptime(payment_expiry, '%Y-%m-%d %H:%M:%S')
                if datetime.now() < expiry_date:
                    # Оплаченный период активен
                    send_app_link(message.chat.id)
                    logger.info(f'User {message.chat.id} accessed with active payment.')
                else:
                    # Оплаченный период истек
                    cursor.execute("UPDATE users SET payment_expiry=? WHERE user_id=?", (None, message.chat.id))
                    conn.commit()
                    check_launches(message, launches_left)
            else:
                check_launches(message, launches_left)
        else:
            # Пользователь не найден в базе данных, добавляем его
            cursor.execute("INSERT INTO users (user_id, launches_left, payment_expiry) VALUES (?, ?, ?)",
                           (message.chat.id, 1, None))
            conn.commit()
            send_app_link(message.chat.id)
            logger.info(f'New user {message.chat.id} accessed, launches left: 1.')
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте предоставленные кнопки.")
        logger.info(f'User {message.chat.id} sent an unknown command.')

def check_launches(message, launches_left):
    if launches_left > 0:
        launches_left -=1
        cursor.execute("UPDATE users SET launches_left=? WHERE user_id=?", (launches_left, message.chat.id))
        conn.commit()
        send_app_link(message.chat.id)
        logger.info(f'User {message.chat.id} accessed, launches left: {launches_left}.')
    else:
        message_text = f"Ваши бесплатные запуски закончились. Пожалуйста, сделайте платеж в размере {PAYMENT_AMOUNT} TON на кошелек {TON_WALLET}, чтобы продолжить."
        bot.send_message(message.chat.id, message_text)
        logger.info(f'User {message.chat.id} attempted to access without remaining launches.')

# Обработчик подтверждения оплаты
@bot.message_handler(commands=['confirm_payment'])
def confirm_payment(message):
    user_id = message.chat.id
    # Здесь вы должны проверить, поступил ли платеж от этого пользователя на ваш счёт TON
    # Если платеж подтвержден, обновите payment_expiry для пользователя
    payment_expiry = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE users SET payment_expiry=? WHERE user_id=?", (payment_expiry, user_id))
    conn.commit()
    bot.send_message(user_id, "Платеж подтвержден! Вы можете использовать приложение в течение одного месяца.")
    logger.info(f'Payment from user {user_id} confirmed.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(non_stop=True)
    logger.info("Bot started and is waiting for messages...")
    print("Bot started and is waiting for messages...")
