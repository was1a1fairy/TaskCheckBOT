from aiogram import filters, Router, F, types
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
import services.basic
import db

router = Router()

class States(StatesGroup):
    name = State()
    deadline = State()
    priority = State()
    note = State()

class StateView(StatesGroup):
    pass


@router.message(filters.Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.button(text="добавить задачу!",
                        callback_data="add_task")

    builder.button(text="список задач",
                   callback_data="view_tasks")

    builder.button(text="помощь",
                   callback_data="help")

    builder.adjust(2)

    await message.answer("Я позволю эффективно управлять личными задачами,"
                        "устанавливать дедлайны и приоритеты, а также"
                        "получать напоминания о приближении сроков."
                        "Давай добавим первую задачу!",
                         reply_markup=builder.as_markup(),

                         )


@router.callback_query(F.data=="add_task")
async def add_task(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.answer("Придумайте название вашей задаче:")
    await callback.answer()
    await state.set_state(States.name)


@router.message(States.name)
async def name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text.strip())
    await message.reply("Супер! Теперь укажи до какого числа нужно выполнить задачу"
                        "(дедлайн указывается в формате дд/мм/гггг)")
    await state.set_state(States.deadline)



@router.message(States.deadline)
async def deadline(message: types.Message, state:FSMContext):
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
    await state.update_data(priority=callback.data)
    await callback.message.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await callback.answer()
    await state.set_state(States.note)


@router.callback_query(F.data=="medium")
async def priority2(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.data)
    await callback.message.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await callback.answer()
    await state.set_state(States.note)


@router.callback_query(F.data=="low")
async def priority3(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.data)
    await callback.message.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await callback.answer()
    await state.set_state(States.note)


@router.message(States.note)
async def note(message: types.Message, state:FSMContext):
    await state.update_data(note=message.text.strip())
    await services.basic.add_task(await state.get_data(), message.from_user.id)
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

    await callback.message.answer("Выберите действие:",
                          reply_markup=builder.as_markup()
                          )

    await callback.answer()


@router.callback_query(F.data=="sort")
async def sort(callback: CallbackQuery):
    await callback.message.reply(f"""{await services.basic.view_tasks(callback.from_user.id)}""")


@router.callback_query(F.data=="first_new")
async def first_new(callback: CallbackQuery):
    await callback.message.reply(f"""{await services.basic.view_tasks(callback.from_user.id, "created_at", "DESC")}""")


@router.callback_query(F.data=="first_old")
async def first_old(callback: CallbackQuery):
    await callback.message.reply(f"""{await services.basic.view_tasks(callback.from_user.id,"created_at", "ASC")}""")



# других хендлеров не будет
@router.message(lambda message: True)
async def handler(message: types.Message):
    await message.reply("воспользуйтесь пожалуйста существующей командой\n/help")