import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔐 ENV переменные (Railway)
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not TOKEN:
    raise ValueError("TOKEN не найден в ENV переменных")

if ADMIN_CHAT_ID == 0:
    raise ValueError("ADMIN_CHAT_ID не найден в ENV переменных")

# 🧠 состояние пользователей
user_state = {}

# 📌 клавиатура
keyboard = ReplyKeyboardMarkup(
    [
        ["📄 Услуги", "⏱ Сроки"],
        ["📎 Оформить заявку", "💶 Стоимость"],
        ["💬 Консультация", "📍 Контакты"],
        ["❓ FAQ"],
    ],
    resize_keyboard=True,
)

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот бюро присяжных переводов 📄\n"
        "Выберите нужный раздел:",
        reply_markup=keyboard,
    )

# 📎 ФАЙЛЫ
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if update.message.document:
        file_type = "PDF/документ"
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_type = "Фото"
        file_id = update.message.photo[-1].file_id
    else:
        return

    # клиенту
    await update.message.reply_text(
        "Файл получен 📄\n"
        "Мы проверим его и свяжемся с вами."
    )

    # админу
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📥 Новая заявка\n"
            f"👤 {user.full_name}\n"
            f"📎 Тип: {file_type}"
        ),
    )

    # пересылка файла
    if update.message.document:
        await context.bot.send_document(ADMIN_CHAT_ID, file_id)
    else:
        await context.bot.send_photo(ADMIN_CHAT_ID, file_id)

# 💬 ТЕКСТ
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📄 Услуги":
        await update.message.reply_text(
            "Присяжные переводы в Испании:\n"
            "• свидетельства\n• дипломы\n• справки\n• документы"
        )

    elif text == "⏱ Сроки":
        await update.message.reply_text(
            "Сроки:\n"
            "• 1–3 дня стандартные документы\n"
            "• 5–7 дней сложные случаи\n\n"
            "Точный срок после проверки."
        )

    elif text == "💶 Стоимость":
        await update.message.reply_text(
            "Стоимость от XX €\n"
            "Точная цена после анализа документов."
        )

   

    elif text == "💬 Консультация":
        await update.message.reply_text(
            "👉 https://t.me/your_manager_username"
        )

    elif text == "📍 Контакты":
        await update.message.reply_text(
            "Напишите нам прямо в чат 📩"
        )

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "FAQ скоро будет добавлен 📌"
        )

    # 🧾 ОФОРМЛЕНИЕ ЗАЯВКИ — ШАГ 1
    elif text == "📎 Оформить заявку":
        user_state[user_id] = "waiting_lang_before_doc"
        await update.message.reply_text(
            "С какого языка требуется перевод? 🌍"
        )

    # 🧾 ШАГ 2 — язык получен
    elif user_state.get(user_id) == "waiting_lang_before_doc":
        user_state[user_id] = "waiting_doc"
        user_state[f"{user_id}_lang"] = text

        await update.message.reply_text(
            "Отлично 👍\nТеперь отправьте документ (PDF или фото) 📄"
        )

    # 🧾 ШАГ 3 — финал
    elif user_state.get(user_id) == "waiting_doc":
        user_state[user_id] = "done"
        await update.message.reply_text(
            "Заявка принята ✅\n"
            "Мы свяжемся с вами."
        )

    else:
        await update.message.reply_text("Выберите пункт меню 👇")


# 🧩 СБОРКА БОТА
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
