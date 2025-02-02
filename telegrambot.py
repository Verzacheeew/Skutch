import os
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_polling
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def download_video(url, format):
    options = {
        'format': format,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Отправь ссылку на видео с YouTube")

@dp.message_handler()
async def get_url(message: types.Message):
    url = message.text
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎵 MP3 (Аудио)", callback_data=f"audio|{url}"),
        InlineKeyboardButton("📹 MP4 (Видео)", callback_data=f"video|{url}")
    )
    await message.reply("Выбери формат:", reply_markup=keyboard)

@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    data, url = callback_query.data.split('|')
    if data == "audio":
        file = download_video(url, "bestaudio/best")
    else:
        file = download_video(url, "best")
    
    await bot.send_document(callback_query.from_user.id, open(file, 'rb'))
    os.remove(file)

if __name__ == "__main__":
    asyncio.run(dp.start_polling())
