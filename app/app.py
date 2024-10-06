import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telebot import TeleBot, types

# Получение токена из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не установлена.")

bot = TeleBot(TOKEN)

# Настройка логирования
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'telegram_bot.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

# Получаем URL приложения из переменной окружения
APP_URL = os.getenv('APP_URL', 'https://yourdomain.com/index.html')  # Замените на ваш реальный HTTPS URL

print("Bot is starting...")
logger.info("Bot is starting...")

# Инициализируем базу данных SQLite
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        launches_left INTEGER,
        payment_expiry TEXT
    )
''')
conn.commit()

# Стоимость и номер счёта для оплаты
PAYMENT_AMOUNT = 0.2  # Стоимость в TONCOIN
TON_WALLET = 'ВАШ_НОМЕР_СЧЁТА_TON'  # Замените на ваш номер счёта

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Support"))
    keyboard.add(types.KeyboardButton("Запуск"))  # Изменено с "Launch" на "Запуск"
    bot.send_message(
        message.chat.id,
        f'Hello, {user.first_name}!',
        reply_markup=keyboard
    )
    logger.info(f'Sent welcome message to user {message.chat.id}')
    print(f"Sent welcome message to user {message.chat.id}")

    # Добавляем пользователя в базу данных, если его там нет
    cursor.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    user_data = cursor.fetchone()
    if not user_data:
        cursor.execute(
            "INSERT INTO users (user_id, launches_left, payment_expiry) VALUES (?, ?, ?)",
            (message.chat.id, 2, None)
        )
        conn.commit()
        logger.info(f'Added new user {message.chat.id} to the database.')
        print(f"Added new user {message.chat.id} to the database.")

# Обработчик нажатий кнопок
@bot.message_handler(func=lambda message: True)
def on_click(message):
    text = message.text
    if text == 'Support':
        message_text = (
            f"To continue using the application after 2 free launches, "
            f"please make a payment of {PAYMENT_AMOUNT} TON to the wallet {TON_WALLET}."
        )
        bot.send_message(message.chat.id, message_text)
        logger.info(f'Sent support message to user {message.chat.id}')
        print(f"Sent support message to user {message.chat.id}")

    elif text == 'Запуск':  # Обработка кнопки "Запуск"
        cursor.execute(
            "SELECT launches_left, payment_expiry FROM users WHERE user_id=?",
            (message.chat.id,)
        )
        user_data = cursor.fetchone()
        if user_data:
            launches_left, payment_expiry = user_data
            if payment_expiry:
                # Проверяем, активен ли оплаченный период
                expiry_date = datetime.strptime(payment_expiry, '%Y-%m-%d %H:%M:%S')
                if datetime.now() < expiry_date:
                    # Оплаченный период активен
                    send_web_app_button(message.chat.id, "Вы уже оплатили доступ до "
                                                           f"{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}.")
                    logger.info(f'User {message.chat.id} accessed with active payment.')
                else:
                    # Оплаченный период истек
                    cursor.execute(
                        "UPDATE users SET payment_expiry=? WHERE user_id=?",
                        (None, message.chat.id)
                    )
                    conn.commit()
                    logger.info(f'Payment period expired for user {message.chat.id}. Resetting payment_expiry.')
                    check_launches(message, launches_left)
            else:
                check_launches(message, launches_left)
        else:
            # Пользователь не найден в базе данных, добавляем его
            cursor.execute(
                "INSERT INTO users (user_id, launches_left, payment_expiry) VALUES (?, ?, ?)",
                (message.chat.id, 1, None)
            )
            conn.commit()
            send_web_app_button(message.chat.id, "Добро пожаловать! У вас 1 запуск.")
            logger.info(f'New user {message.chat.id} accessed, launches left: 1.')
    else:
        bot.send_message(message.chat.id, "Please use the provided buttons.")
        logger.info(f'User {message.chat.id} sent an unknown command.')

def check_launches(message, launches_left):
    if launches_left > 0:
        launches_left -= 1
        cursor.execute(
            "UPDATE users SET launches_left=? WHERE user_id=?",
            (launches_left, message.chat.id)
        )
        conn.commit()
        send_web_app_button(message.chat.id, f"Запуск выполнен. Осталось запусков: {launches_left}.")
        logger.info(f'User {message.chat.id} accessed, launches left: {launches_left}.')
    else:
        message_text = (
            f"Your free launches are over. Please make a payment of {PAYMENT_AMOUNT} TON "
            f"to the wallet {TON_WALLET} to continue."
        )
        bot.send_message(message.chat.id, message_text)
        logger.info(f'User {message.chat.id} attempted to access without remaining launches.')

def send_web_app_button(chat_id, text):
    """
    Отправляет сообщение с кнопкой для открытия веб-приложения.
    """
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Открыть веб-приложение", url=APP_URL)
    markup.add(button)
    bot.send_message(chat_id, text, reply_markup=markup)

# Обработчик подтверждения оплаты
@bot.message_handler(commands=['confirm_payment'])
def confirm_payment(message):
    user_id = message.chat.id
    # Здесь вы должны проверить, поступил ли платеж от этого пользователя на ваш счёт TON
    # Если платеж подтвержден, обновите payment_expiry для пользователя
    payment_expiry = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "UPDATE users SET payment_expiry=? WHERE user_id=?",
        (payment_expiry, user_id)
    )
    conn.commit()
    bot.send_message(user_id, "Payment confirmed! You can use the application for one month.")
    logger.info(f'Payment from user {user_id} confirmed.')

# Запуск бота
if __name__ == '__main__':
    try:
        logger.info("Запуск поллинга...")
        print("Bot started and is waiting for messages...")
        bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
