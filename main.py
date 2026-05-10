
import aiogram
from aiogram import Dispatcher
import asyncio

from db import Repo
from secret_data import token
import handlers
from handlers import basic, login, main, optional, register
import middleware
from middleware import register




bot = aiogram.Bot(token)
dp = Dispatcher()



async def main():
    dp.update.outer_middleware(middleware.register.Register())
    dp.include_routers(basic.router)
    dp.include_routers(handlers.main.router)
    dp.include_routers(optional.router)
    dp.include_routers(handlers.register.router)
    dp.include_routers(login.router)
    repo = Repo("repo.db")
    try:
        await repo.connect()
        await dp.start_polling(bot, repo=repo)
    finally:
        await repo.close()

if __name__ == '__main__':
    asyncio.run(main())