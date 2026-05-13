import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не найден в .env файле')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def echo_handler(message):
    await message.answer(message.text)

@dp.message()
async def hello_handler(message = 'Hi'):
    await message.answer('HELLOOOOO')

async def main():
    print('Bot is running...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())