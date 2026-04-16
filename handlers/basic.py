
from aiogram import filters, Router, F, types

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router1 = Router()


@router1.message(filters.Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.button(text="добавить задачу!",
                        callback_data="добавить задачу")

    builder.button(text="список задач",
                   callback_data="список задач")

    builder.button(text="помощь",
                   callback_data="help")

    builder.adjust(1)

    await message.answer("Я позволю эффективно управлять личными задачами,"
                        "устанавливать дедлайны и приоритеты, а также"
                        "получать напоминания о приближении сроков."
                        "Давай добавим задачу!",
                         reply_markup=builder.as_markup()
                         )


@router1.callback_query(F.data=="help")
async def helpp(callback: CallbackQuery, state: FSMContext):
    await callback.message.reply(f"""Тебе нужна помощь?
    Давай объясню что я умею и покажу как пользоваться моими командами!\n
    Нажми добавить задачу, последовательно выбирай настройки
    Добавляй нужное количество задач и отслеживай их через "список задач" в меню!""")
    await state.clear()


@router1.callback_query(F.data=="exit")
async def exitt(callback:CallbackQuery,state: FSMContext):
    builder = InlineKeyboardBuilder()

    builder.button(text="добавить задачу!",
                        callback_data="добавить задачу")

    builder.button(text="список задач",
                   callback_data="список задач")

    builder.button(text="помощь",
                   callback_data="help")

    builder.adjust(1)

    await callback.message.answer("Я позволю эффективно управлять личными задачами,"
                        "устанавливать дедлайны и приоритеты, а также"
                        "получать напоминания о приближении сроков."
                        "Давай добавим задачу!",
                         reply_markup=builder.as_markup()
                         )
    await callback.answer()

    await state.clear()