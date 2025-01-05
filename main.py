import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
from config import BOT_TOKEN  # Импортируем токен из config.py

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Список случайных фактов
FACTS = [
    "Человеческий мозг генерирует достаточно электричества, чтобы зажечь лампочку.",
    "Кошки мурлыкают с частотой, которая может способствовать заживлению костей и тканей.",
    "В Антарктиде есть водопад, который течет красной водой, его называют Кровавым водопадом.",
    "Самая старая живая вещь на Земле — это дерево возрастом более 5000 лет.",
    "Шмели способны запоминать лица.",
    "Осьминоги имеют три сердца, и их кровь синего цвета.",
]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот, который знает много интересных фактов. Напиши /fact, чтобы узнать что-то новое!"
    )

# Команда /fact
async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_fact = random.choice(FACTS)
    await update.message.reply_text(random_fact)

# Основной код
if __name__ == "__main__":
    # Используем токен из config.py
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fact", fact))

    # Запускаем бота
    application.run_polling()
