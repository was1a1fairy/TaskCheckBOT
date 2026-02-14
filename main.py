
import aiogram
from aiogram import Dispatcher
import asyncio

from secret_data import token
import handlers.basic




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():

    dp.include_routers(handlers.basic.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())