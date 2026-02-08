from ipaddress import summarize_address_range

import aiogram
from aiogram import filters, Dispatcher
import asyncio
from aiogram import F
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

import db
from secret_data import token
import handlers.basic




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():

    dp.include_routers(handlers.basic.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())