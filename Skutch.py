import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube

# Получение токена из переменной окружения или напрямую из ко
TELEGRAM_BOT_TOKEN = "8135335284:AAH3fc_o0GIg-vl7ntCQJ_r16ZUep9Vap0Q"  # Замените на реальный токен# Замените на реальный токен  # Замените на реальный токен

# Глобальная переменная для хранения ссылки на видео
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне ссылку на YouTube-видео.")

# Обработка текстовых сообщений (ссылка на YouTube)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        # Проверяем, является ли ссылка валидной
        yt = YouTube(url)
        title = yt.title
        user_data[update.effective_chat.id] = {"url": url, "title": title}
        await update.message.reply_text(f"Видео найдено: {title}")

        # Предлагаем выбрать формат
        keyboard = [
            [InlineKeyboardButton("MP4 (Видео)", callback_data="mp4")],
            [InlineKeyboardButton("MP3 (Аудио)", callback_data="mp3")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите формат:", reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text("Неверная ссылка или видео недоступно.")

# Обработка выбора формата
async def handle_format_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id not in user_data:
        await query.answer("Произошла ошибка. Попробуйте снова.")
        return

    format_choice = query.data
    user_data[chat_id]["format"] = format_choice

    if format_choice == "mp4":
        # Предлагаем выбрать качество видео
        keyboard = [
            [InlineKeyboardButton("240p", callback_data="240p")],
            [InlineKeyboardButton("360p", callback_data="360p")],
            [InlineKeyboardButton("480p", callback_data="480p")],
            [InlineKeyboardButton("720p", callback_data="720p")],
            [InlineKeyboardButton("1080p", callback_data="1080p")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите качество видео:", reply_markup=reply_markup)

    elif format_choice == "mp3":
        # Предлагаем выбрать битрейт аудио
        keyboard = [
            [InlineKeyboardButton("128 kbps", callback_data="128kbps")],
            [InlineKeyboardButton("192 kbps", callback_data="192kbps")],
            [InlineKeyboardButton("256 kbps", callback_data="256kbps")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите битрейт аудио:", reply_markup=reply_markup)

# Обработка выбора качества/битрейта
async def handle_quality_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id not in user_data:
        await query.answer("Произошла ошибка. Попробуйте снова.")
        return

    choice = query.data
    user_data[chat_id]["quality"] = choice

    # Скачиваем видео/аудио
    url = user_data[chat_id]["url"]
    format_choice = user_data[chat_id]["format"]

    try:
        yt = YouTube(url)
        if format_choice == "mp4":
            # Скачиваем видео
            stream = yt.streams.filter(res=choice, file_extension="mp4").first()
            file_path = stream.download(output_path="downloads")
            await query.edit_message_text("Видео загружено. Отправляю...")
        elif format_choice == "mp3":
            # Скачиваем аудио
            audio_stream = yt.streams.filter(only_audio=True).first()
            file_path = audio_stream.download(output_path="downloads")
            new_file_path = os.path.splitext(file_path)[0] + ".mp3"
            os.rename(file_path, new_file_path)
            file_path = new_file_path
            await query.edit_message_text("Аудио загружено. Отправляю...")

        # Отправляем файл пользователю
        with open(file_path, "rb") as file:
            await context.bot.send_document(chat_id=chat_id, document=file)

        # Удаляем файл после отправки
        os.remove(file_path)

    except Exception as e:
        await query.edit_message_text("Произошла ошибка при скачивании.")

# Основная функция
def main():
    # Создание приложения
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_format_choice, pattern="^(mp4|mp3)$"))
    application.add_handler(CallbackQueryHandler(handle_quality_choice, pattern="^(240p|360p|480p|720p|1080p|128kbps|192kbps|256kbps)$"))

    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
