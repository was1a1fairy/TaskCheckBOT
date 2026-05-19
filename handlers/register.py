
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.for_handlers import for_register
from db import Repo

router = Router()


class StatesREG(StatesGroup):
    username = State()
    email = State()
    password = State()


@router.message(F.text == "зарегистрироваться")
async def register(message: types.Message, state: FSMContext) -> None:
    """Начинает процесс регистрации"""
    await message.reply("Придумайте ник:")
    await state.set_state(StatesREG.username)


@router.message(StatesREG.username)
async def try_username(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет username и запрашивает email"""
    if await for_register.check_username(message.text, repo):
        await state.update_data(username=message.text.strip())
        await message.reply("Ник добавлен успешно, теперь введите почту!")
        await state.set_state(StatesREG.email)
    else:
        await message.reply("Ник должен быть из англ букв от 3 до 20 символов или уже используется! Попробуйте новый")


@router.message(StatesREG.email)
async def try_email(message: types.Message, state: FSMContext) -> None:
    """Проверяет email и запрашивает пароль"""
    if await for_register.check_email(message.text):
        await state.update_data(email=message.text.strip())
        await message.reply("Почтовый адрес добавлен успешно, теперь придумайте пароль!")
        await state.set_state(StatesREG.password)
    else:
        await message.reply("Почтовый адрес не прошел валидацию, возможно вы допустили ошибку или он уже используется! Попробуйте снова")


@router.message(StatesREG.password)
async def try_password(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет пароль и завершает регистрацию"""
    if await for_register.check_password(message.text):
        await state.update_data(password=message.text.strip())
        await for_register.register(await state.get_data(), message.from_user.id, repo)
        await message.reply("Регистрация завершена! Нажмите /start для начала работы")
        await state.clear()
    else:
        await message.reply("Пароль слишком длинный или содержит символы помимо латинских букв и цифр! Попробуйте новый")