from aiogram import filters, Router, F, types
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
import services
import db

router = Router()

class States(StatesGroup):
    name = State()
    deadline = State()
    priority = State()
    note = State()

@router.message(filters.Command("start"))
async def start(message: types.Message, command: filters.CommandObject):
    builder = InlineKeyboardBuilder()

    builder.button(text="добавить задачу!",
                        callback_data="add_task")

    builder.button(text="посмотреть существующие задачи...",
                   callback_data="view_tasks")

    builder.button(text="посмотреть список команд с инструкциями",
                   callback_data="help")

    await message.answer("Я позволю эффективно управлять личными задачами,"
                        "устанавливать дедлайны и приоритеты, а также"
                        "получать напоминания о приближении сроков."
                        "Давай добавим первую задачу!",
                         reply_markup=builder.as_markup()
                         )


@router.callback_query(F.data=="add_task")
async def add_task(callback: types.CallbackQuery, state:FSMContext):
    await callback.answer("Придумайте название вашей задаче:")
    await state.set_state(States.name)


@router.message(state = States.name)
async def name(message: types.Message, command: filters.CommandObject, state:FSMContext):
    await state.update_data(name=message.text.strip())
    await message.reply("Супер! Теперь укажи до какого числа нужно выполнить задачу"
                        "(дедлайн указывается в формате дд/мм/гггг)")
    await state.set_state(States.deadline)



@router.message(state = States.deadline)
async def deadline(message: types.Message, command: filters.CommandObject, state:FSMContext):
    await state.update_data(deadline=message.text.strip())
    builder = InlineKeyboardBuilder()

    builder.button(text="высокий",
                   callback_data="high")

    builder.button(text="средний",
                   callback_data="medium")

    builder.button(text="низкий",
                   callback_data="low")

    await message.answer("Выбери приоритет для этой задачи:",
                         reply_markup=builder.as_markup()
                         )
    await state.set_state(States.priority)


@router.callback_query(F.data=="high")
async def priority1(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.text.strip())
    await callback.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await state.set_state(States.note)


@router.callback_query(F.data=="medium")
async def priority2(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.text.strip())
    await callback.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await state.set_state(States.note)


@router.callback_query(F.data=="low")
async def priority3(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.text.strip())
    await callback.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await state.set_state(States.note)


@router.message(state=States.note)
async def note(message: types.Message, command: filters.CommandObject, state:FSMContext):
    await state.update_data(priority=message.text.strip())
    await services.basic.add_task(state.get_data(), message.from_user.id)
    await state.clear()


@router.callback_query(F.data=="view_tasks")
async def view_tasks(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.button(text="сортировка по умолчанию",
                   callback_data="sort")

    builder.button(text="сначала новые задачи",
                   callback_data="first_new")

    builder.button(text="сначала старые задачи",
                   callback_data="first_old")

    builder.button(text="сортировка по одному из параметров",
                   callback_data="chose_param")

    builder.button(text="выйти из создания задачи",
                   callback_data="exit")

    await callback.answer("Выберите действие:",
                          reply_markup=builder.as_markup()
                          )








# других хендлеров не будет
@router.message(lambda message: True)
async def handler(message: types.Message):
    await message.reply("воспользуйтесь пожалуйста существующей командой\n/help")