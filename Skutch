import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from pytube import YouTube
from moviepy.editor import VideoFileClip

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для хранения выбранных параметров пользователей
user_data = {}

# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку на YouTube видео, и я помогу скачать его в MP4 или MP3 формате.")

# Обработка сообщений с ссылкой
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id

    try:
        yt = YouTube(url)
        video_title = yt.title
        user_data[user_id] = {'url': url, 'title': video_title}

        # Создаем кнопки для выбора формата
        keyboard = [
            [InlineKeyboardButton("MP4", callback_data="mp4")],
            [InlineKeyboardButton("MP3", callback_data="mp3")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"Видео: {video_title}\nВыберите формат:", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке ссылки: {e}")
        await update.message.reply_text("Неверная ссылка или видео недоступно.")

# Обработка выбора формата
async def format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data
    user_data[user_id]['format'] = data

    if data == "mp4":
        # Создаем кнопки для выбора качества видео
        keyboard = [
            [InlineKeyboardButton("240p", callback_data="240"), InlineKeyboardButton("360p", callback_data="360")],
            [InlineKeyboardButton("480p", callback_data="480"), InlineKeyboardButton("720p", callback_data="720")],
            [InlineKeyboardButton("1080p", callback_data="1080")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите качество видео:", reply_markup=reply_markup)

    elif data == "mp3":
        # Создаем кнопки для выбора битрейта аудио
        keyboard = [
            [InlineKeyboardButton("128kbps", callback_data="128"), InlineKeyboardButton("192kbps", callback_data="192")],
            [InlineKeyboardButton("256kbps", callback_data="256"), InlineKeyboardButton("320kbps", callback_data="320")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите битрейт аудио:", reply_markup=reply_markup)

# Обработка выбора качества/битрейта
async def quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data
    user_data[user_id]['quality'] = data

    if user_data[user_id]['format'] == "mp4":
        await download_video(update, context)
    elif user_data[user_id]['format'] == "mp3":
        await download_audio(update, context)

# Скачивание видео
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    url = user_data[user_id]['url']
    quality = user_data[user_id]['quality']

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(res=f"{quality}p", file_extension="mp4").first()
        if not stream:
            await query.edit_message_text("Видео в выбранном качестве недоступно.")
            return

        file_path = f"{yt.title}_{quality}p.mp4"
        stream.download(filename=file_path)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(chat_id=user_id, video=video_file, caption=f"Видео ({quality}p): {yt.title}")

        os.remove(file_path)  # Удаляем файл после отправки
        await query.edit_message_text("Видео успешно отправлено!")

    except Exception as e:
        logger.error(f"Ошибка при скачивании видео: {e}")
        await query.edit_message_text("Произошла ошибка при скачивании видео.")

# Скачивание аудио
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    url = user_data[user_id]['url']
    bitrate = user_data[user_id]['quality']

    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(only_audio=True).first()
        temp_file = f"{yt.title}_temp.mp4"
        video_stream.download(filename=temp_file)

        # Конвертация в MP3
        audio_file = f"{yt.title}_{bitrate}kbps.mp3"
        clip = VideoFileClip(temp_file)
        clip.audio.write_audiofile(audio_file, bitrate=f"{bitrate}k")
        clip.close()

        with open(audio_file, 'rb') as audio:
            await context.bot.send_audio(chat_id=user_id, audio=audio, caption=f"Аудио ({bitrate}kbps): {yt.title}")

        os.remove(temp_file)  # Удаляем временный файл
        os.remove(audio_file)  # Удаляем файл после отправки
        await query.edit_message_text("Аудио успешно отправлено!")

    except Exception as e:
        logger.error(f"Ошибка при скачивании аудио: {e}")
        await query.edit_message_text("Произошла ошибка при скачивании аудио.")

# Основная функция
def main():
    token = "8135335284:AAH3fc_o0GIg-vl7ntCQJ_r16ZUep9Vap0Q"  # Замените на токен вашего бота
    application = ApplicationBuilder().token(token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.add_handler(CallbackQueryHandler(format_selection, pattern="^(mp4|mp3)$"))
    application.add_handler(CallbackQueryHandler(quality_selection, pattern="^(240|360|480|720|1080|128|192|256|320)$"))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
