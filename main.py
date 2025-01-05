from config import BOT_TOKEN
import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Функции бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🎵 Hello! I am your Music Bot.\n"
        "Here's what I can do:\n"
        "Type any song name, and I'll try to find it for you!"
    )

async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Поиск песни по названию."""
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("❌ Please enter a song name to search!")
        return

    # Пример использования API для поиска песни (в данном случае Deezer API)
    try:
        response = requests.get(f"https://api.deezer.com/search?q={query}")
        response.raise_for_status()
        data = response.json()
        if data["data"]:
            song = data["data"][0]  # Берём первый результат
            song_title = song["title"]
            artist = song["artist"]["name"]
            preview_url = song["preview"]

            if preview_url:
                await update.message.reply_audio(
                    audio=preview_url,
                    caption=f"🎧 {song_title} by {artist}"
                )
            else:
                await update.message.reply_text(f"🎵 Found: {song_title} by {artist}, but no preview is available.")
        else:
            await update.message.reply_text("❌ No results found. Try another song.")
    except Exception as e:
        logger.error(f"Error while searching song: {e}")
        await update.message.reply_text("❌ An error occurred while searching for the song. Please try again later.")

# --- Основной код ---
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_song))

    # Запуск бота
    logger.info("Music bot is running. Waiting for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
