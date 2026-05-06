
import aiogram
from aiogram import Dispatcher
import asyncio

from secret_data import token
import handlers
import middleware




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():
    dp.update.outer_middleware(middleware.register.Register)
    dp.include_routers(handlers.basic.router1)
    dp.include_routers(handlers.main.router2)
    dp.include_routers(handlers.optional.router3)
    dp.include_routers(handlers.register.router4)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())