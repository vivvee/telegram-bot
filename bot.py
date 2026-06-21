from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

# 🔐 Токен берётся из переменной окружения
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не найдена!")

# 👤 Твой Telegram ID
ADMIN_CHAT_ID = 1137467971

# Хранение состояния пользователей
user_state = {}

# Кнопки меню
keyboard = ReplyKeyboardMarkup(
    [
        ["📄 Услуги", "⏱ Сроки"],
        ["📎 Оставить заявку", "💶 Стоимость"],
        ["💬 Консультация", "📍 Контакты"],
        ["📘 Апостиль", "⚡ Срочный заказ"],
    ],
    resize_keyboard=True,
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот бюро присяжных переводов 📄\n"
        "Выберите, что вас интересует:",
        reply_markup=keyboard,
    )

# Обработка файлов
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if update.message.document:
        file_type = "PDF/документ"
    elif update.message.photo:
        file_type = "Фото"
    else:
        return

    # Ответ клиенту
    await update.message.reply_text(
        "Файл получен 📄\n"
        "Мы проверим его и свяжемся с вами."
    )

    # Уведомление админу
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📥 Новая заявка\n"
            f"👤 {user.full_name}\n"
            f"📎 Тип: {file_type}"
        ),
    )

    # Пересылаем файл
    if update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=update.message.document.file_id,
        )

    elif update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
        )

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📄 Услуги":
        await update.message.reply_text(
            "Мы выполняем присяжные переводы в Испании:\n"
            "• свидетельства\n"
            "• дипломы\n"
            "• справки\n"
            "• юридические документы"
        )

    elif text == "⏱ Сроки":
        await update.message.reply_text(
            "Сроки выполнения:\n"
            "• 1–3 рабочих дня — стандартные документы\n"
            "• до 5–7 дней — сложные случаи\n\n"
            "Точный срок сообщим после проверки документов."
        )

    elif text == "💶 Стоимость":
        await update.message.reply_text(
            "Стоимость начинается от XX €.\n"
            "Точную цену сообщим после проверки документов."
        )

    elif text == "📘 Апостиль":
        await update.message.reply_text(
            "Мы помогаем оформить апостиль и выполнить присяжный перевод."
        )

    elif text == "💬 Консультация":
        await update.message.reply_text(
            "Напишите свой вопрос, и мы обязательно ответим."
        )

    elif text == "📍 Контакты":
        await update.message.reply_text(
            "Напишите нам прямо здесь, в Telegram."
        )

    elif text == "⚡ Срочный заказ":
        await update.message.reply_text(
            "⚡ Срочный заказ принят.\n"
            "Мы обработаем его в приоритетном порядке."
        )

    elif text == "📎 Оставить заявку":
        user_state[user_id] = "waiting_doc"
        await update.message.reply_text(
            "Отправьте фотографию или PDF документа."
        )

    elif user_state.get(user_id) == "waiting_doc":
        user_state[user_id] = "waiting_lang"
        await update.message.reply_text(
            "На какой язык нужен перевод?"
        )

    elif user_state.get(user_id) == "waiting_lang":
        user_state[user_id] = "done"
        await update.message.reply_text(
            "Спасибо! ✅\n"
            "Мы получили заявку и скоро свяжемся с вами."
        )

    else:
        await update.message.reply_text(
            "Выберите пункт меню ниже 👇"
        )

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file)
)
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
)

# Запуск
if __name__ == "__main__":
    print("Бот запускается...")
    app.run_polling()
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()
