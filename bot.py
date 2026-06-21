from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import os

TOKEN = os.getenv("TOKEN")

# 👉 сюда вставишь свой Telegram ID (мы его получим ниже)
ADMIN_CHAT_ID = 1137467971

# 🧠 хранение простого состояния диалога
user_state = {}

# 📌 КНОПКИ МЕНЮ
keyboard = ReplyKeyboardMarkup(
    [
        ["📄 Услуги", "⏱ Сроки"],
        ["📎 Оставить заявку", "💶 Стоимость"],
        ["💬 Консультация", "📍 Контакты"],
        ["📘 Апостиль", "⚡ Срочный заказ"],
    ],
    resize_keyboard=True
)

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот бюро присяжных переводов 📄\n"
        "Выберите, что вас интересует:",
        reply_markup=keyboard
    )

# 📎 ОБРАБОТКА ФАЙЛОВ
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    file = None

    if update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        file_type = "PDF/документ"

    elif update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_type = "Фото"

    # 📤 клиенту
    await update.message.reply_text(
        "Файл получен 📄\nМы проверим и свяжемся с вами."
    )

    # 📥 ТЕБЕ — ВОТ ГЛАВНОЕ
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📥 Новая заявка\n"
             f"👤 {user.full_name}\n"
             f"📎 Тип: {file_type}"
    )

    # 👉 отправка самого файла тебе
    if update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=update.message.document.file_id
        )

    elif update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id
        )

# 💬 ТЕКСТОВЫЕ СООБЩЕНИЯ
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # 📄 УСЛУГИ
    if text == "📄 Услуги":
        await update.message.reply_text(
            "Мы выполняем присяжные переводы в Испании:\n"
            "- свидетельства\n- дипломы\n- справки\n- юридические документы"
        )

    # ⏱ СРОКИ
    elif text == "⏱ Сроки":
        await update.message.reply_text(
            "Сроки:\n"
            "- 1–3 рабочих дня стандартные документы\n"
            "- до 5–7 дней сложные случаи\n\n"
            "Точный срок после проверки сканов 📄"
        )

    # 💶 СТОИМОСТЬ
    elif text == "💶 Стоимость":
        await update.message.reply_text(
            "Стоимость от XX€ за документ 📄\n\n"
            "Точная цена после анализа сканов."
        )

    # 📘 АПОСТИЛЬ
    elif text == "📘 Апостиль":
        await update.message.reply_text(
            "Апостиль — международное заверение документа.\n"
            "Мы помогаем оформить его в Испании."
        )

    # 💬 КОНСУЛЬТАЦИЯ
    elif text == "💬 Консультация":
        await update.message.reply_text(
            "Опишите ваш вопрос, мы ответим вам 💬"
        )

    # 📍 КОНТАКТЫ
    elif text == "📍 Контакты":
        await update.message.reply_text(
            "Напишите нам сюда в чат — мы отвечаем быстро 💬"
        )

    # ⚡ СРОЧНЫЙ ЗАКАЗ
    elif text == "⚡ Срочный заказ":
        await update.message.reply_text(
            "⚡ Срочный заказ принят\n"
            "Он будет обработан в приоритетном порядке."
        )

    # 📎 ЗАЯВКА — СТАРТ ВОРОНКИ
    elif text == "📎 Оставить заявку":
        user_state[user_id] = "waiting_doc"
        await update.message.reply_text(
            "Отправьте ваш документ (фото или PDF) 📄"
        )

    # 🧠 ПРОСТАЯ ВОРОНКА
    elif user_state.get(user_id) == "waiting_doc":
        user_state[user_id] = "waiting_lang"
        await update.message.reply_text(
            "Какой язык перевода?"
        )

    elif user_state.get(user_id) == "waiting_lang":
        user_state[user_id] = "done"
        await update.message.reply_text(
            "Заявка принята ✅\n"
            "Мы проверим документы и свяжемся с вами."
        )

    else:
        await update.message.reply_text(
            "Выберите пункт из меню 👇"
        )


# 🧩 СБОРКА БОТА
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
