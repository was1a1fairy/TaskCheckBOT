
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import services.for_handlers.for_login as for_login
from db import Repo

router = Router()


class StatesLOG(StatesGroup):
    username = State()
    password = State()


@router.message(F.text == "войти")
async def login(message: types.Message, state: FSMContext) -> None:
    """Начинает процесс входа в аккаунт"""
    await message.reply("Введите ник:")
    await state.set_state(StatesLOG.username)


@router.message(StatesLOG.username)
async def try_username(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет username и запрашивает пароль"""
    if await for_login.check_username(message.text, repo):
        await state.update_data(username=message.text.strip())
        await message.reply("Аккаунт найден, теперь введите пароль!")
        await state.set_state(StatesLOG.password)
    else:
        await message.reply("Пользователя с таким ником не существует! Попробуйте другой")


@router.message(StatesLOG.password)
async def try_password(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет пароль и завершает вход"""
    user_data = await state.get_data()
    if await for_login.check_password(message.text, user_data["username"], repo):
        await state.update_data(password=message.text.strip())
        await message.reply("Пароль верный, теперь снова нажмите /start !")
        await for_login.login(user_data, message.from_user.id, repo)
        await state.clear()
    else:
        await message.reply("Пароль не подошел! Попробуйте снова")


@router.message(lambda message: True)
async def handler(message: types.Message) -> None:
    """Обрабатывает сообщения, которые не распознаны другими хендлерами"""
    await message.reply("Я не умею распознавать сообщения, воспользуйся пожалуйста командой или меню!\n/exit")
