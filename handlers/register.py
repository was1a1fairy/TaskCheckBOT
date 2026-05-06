
from aiogram import Router, F, types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.for_handlers import for_register

router4 = Router()


class StatesLOG(StatesGroup):
    username = State()
    email = State()
    password = State()



@router4.message(F.text=="зарегистрироваться")
async def register(message:types.Message, state:FSMContext):
    await message.reply("Придумайте ник:")
    await state.set_state(StatesLOG.username)


@router4.message(StatesLOG.username)
async def try_username(message:types.Message, state:FSMContext):
    if for_register.check_username(message.text):
        await state.update_data(username=message.text.strip())
        await message.reply("Ник добавлен успешно, теперь введите почту!")
        await state.set_state(StatesLOG.email)
    else:
        await message.reply("Ник слишком длинный или уже используется! Попробуйте новый")


@router4.message(StatesLOG.email)
async def try_email(message:types.Message, state:FSMContext):
    if for_register.check_email(message.text):
        await state.update_data(email=message.text.strip())
        await message.reply("Почтовый адрес добавлен успешно, теперь придумайте пароль!")
        await state.set_state(StatesLOG.password)
    else:
        await message.reply("Почтовый адрес не прошел валидацию, возможно вы допустили ошибку! Попробуйте снова")


@router4.message(StatesLOG.password)
async def try_password(message:types.Message,state:FSMContext):
    if for_register.check_password(message.text):
        await state.update_data(password=message.text.strip())
        await message.reply("Пароль добавлен успешно, теперь снова нажмите /start !")
        await state.clear()
    else:
        await message.reply("Пароль слишком длинный или содержит символы помимо латинских букв и цифр! Попробуйте новый")