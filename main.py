from config import BOT_TOKEN
import os
import logging
import sqlite3
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список доступных языков
languages = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Russian",
    "es": "🇪🇸 Spanish",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German"
}

# --- Функции для работы с базой данных ---
def init_db():
    """Создаёт таблицу для хранения данных пользователей, если она ещё не создана."""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'en'
        )
    """)
    conn.commit()
    conn.close()

def get_user_language(user_id):
    """Возвращает язык пользователя из базы данных. Если пользователь не найден, возвращает 'en'."""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "en"

def set_user_language(user_id, language):
    """Устанавливает язык пользователя в базе данных."""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, language)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
    """, (user_id, language))
    conn.commit()
    conn.close()

# --- Функции бота ---
# Функция перевода текста через Google Translate API
def translate_text(text, target_language):
    try:
        url = f"https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",  # Исходный язык — английский
            "tl": target_language,  # Целевой язык
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        translated_text = response.json()[0][0][0]
        return translated_text
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        return text  # Если перевод не удался, возвращаем оригинальный текст

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! 👋 I am a bot that can provide you with interesting random facts.\n"
        "Use the /fact command to get a fact or /help for instructions.\n\n"
        "You can also configure the language using the /language command."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Here's what I can do:\n\n"
        "/start - Start the bot\n"
        "/fact - Get a random fact (in your selected language)\n"
        "/language - Choose a language\n"
        "/help - Show this message\n"
    )

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(languages["en"], callback_data='en')],
        [InlineKeyboardButton(languages["ru"], callback_data='ru')],
        [InlineKeyboardButton(languages["es"], callback_data='es')],
        [InlineKeyboardButton(languages["fr"], callback_data='fr')],
        [InlineKeyboardButton(languages["de"], callback_data='de')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select the language you want to receive facts in:",
        reply_markup=reply_markup
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected_language = query.data

    # Сохраняем выбранный язык в базу данных
    set_user_language(user_id, selected_language)

    await query.edit_message_text(
        text=f"✅ You have selected the language: {languages[selected_language]}.\n"
             "From now on, you will receive facts in this language."
    )

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Получаем язык пользователя из базы данных
    lang = get_user_language(user_id)

    # URL API для получения факта
    url = f"https://uselessfacts.jsph.pl/random.json?language=en"  # Всегда получаем факт на английском

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        fact_text = data.get("text", "Unable to retrieve a fact. Please try again later.")

        # Если язык отличается от английского, переводим факт
        if lang != "en":
            fact_text = translate_text(fact_text, lang)

        await update.message.reply_text(f"🤔 Here is your fact:\n\n{fact_text}")
    except Exception as e:
        logger.error(f"Error fetching fact: {e}")
        await update.message.reply_text("An error occurred while retrieving the fact. Please try again later.")

# --- Основной код ---
def main():
    # Инициализация базы данных
    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CallbackQueryHandler(set_language))  # Обработчик выбора языка

    # Запуск бота
    logger.info("Bot is running. Waiting for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
