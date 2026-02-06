from ipaddress import summarize_address_range

import aiogram
from aiogram import filters, Dispatcher
import asyncio
from aiogram import F
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from secret_data import token




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():


    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())