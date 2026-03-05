
import aiogram
from aiogram import Dispatcher
import asyncio

from secret_data import token
import handlers.basic




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():

    dp.include_router1s(handlers.basic.router11)
    dp.include_router1s(handlers.basic.router12)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())