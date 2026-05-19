
from aiogram import filters, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(filters.Command("start"))
async def start(message: types.Message) -> None:
    """Обрабатывает команду /start и показывает главное меню"""
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


@router.callback_query(F.data=="help")
async def helpp(callback: CallbackQuery, state: FSMContext) -> None:
    """Показывает справку"""
    await callback.message.reply(f"""
    Тебе нужна помощь?
    Давай объясню что я умею и покажу как пользоваться моими командами!\n
    Нажми добавить задачу, последовательно выбирай настройки
    Добавляй нужное количество задач и отслеживай их через "список задач" в меню!""")
    await state.clear()


@router.message(Command("exit"))
@router.callback_query(F.data=="exit")
@router.message(lambda message: message.text == "вернуться в начало")
async def exitt(event: CallbackQuery | Message, state: FSMContext) -> None:
    """Возвращает пользователя в главное меню"""
    if isinstance(event,CallbackQuery):
        event = event.message

    builder = InlineKeyboardBuilder()

    builder.button(text="добавить задачу!",
                        callback_data="добавить задачу")

    builder.button(text="список задач",
                   callback_data="список задач")

    builder.button(text="помощь",
                   callback_data="help")

    builder.adjust(1)

    await event.answer("Вы вернулись в начало! "
                        "Я позволю эффективно управлять личными задачами, "
                        "устанавливать дедлайны и приоритеты, а также "
                        "получать напоминания о приближении сроков. "
                        "Давай добавим задачу!",
                         reply_markup=builder.as_markup()
                         )

    await state.clear()
