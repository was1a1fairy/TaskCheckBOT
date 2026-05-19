
import aiogram
from aiogram import Dispatcher
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import services.reminders
from db import Repo
from secret_data import token
import handlers
from handlers import basic, login, main, optional, register
from middleware import register as register_middleware

bot = aiogram.Bot(token)
dp = Dispatcher()


async def main() -> None:
    """Главная функция для запуска бота"""
    repo = Repo("repo.db")
    repo = await repo.connect()
    dp.update.outer_middleware(register_middleware.Register(repo))
    dp.include_routers(basic.router)
    dp.include_routers(handlers.main.router)
    dp.include_routers(optional.router)
    dp.include_routers(handlers.register.router)
    dp.include_routers(login.router)
    
    scheduler = BackgroundScheduler()
    services.reminders.start_reminder_service(scheduler, bot, repo, days=1)
    
    try:
        await dp.start_polling(bot, repo=repo)
    finally:
        scheduler.shutdown()
        await repo.close()

if __name__ == '__main__':
    asyncio.run(main())

