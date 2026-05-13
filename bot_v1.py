import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

bot = Bot(token='8618517359:AAGfwdXogvGjrtJBbSVUVNNGrqgrfNy4TRI')
dp = Dispatcher()

@dp.message()
async def echo_handler(message):
    await message.answer(message.text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())