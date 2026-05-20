
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
🤖 *Что я умею:*

📝 *Добавлять задачи* — с названием, дедлайном, приоритетом и описанием

📋 *Список задач* — просматривать все задачи, сортировать по дате, приоритету, статусу

✏️ *Редактировать* — менять название, дедлайн, приоритет или описание

✅ *Отмечать выполнение* — отмечать задачи как выполненные

🗑️ *Удалять* — удалять ненужные задачи

⏰ *Напоминания* — устанавливать напоминания за 1, 2, 3 дня или неделю до дедлайна

📊 *Аналитика* — смотреть статистику: сколько задач выполнено, процент выполнения, распределение по приоритетам

💡 *Как пользоваться:*
Просто нажимай кнопки в меню и следуй инструкциям! Всё интуитивно понятно 🎯

Команда /exit или "вернуться в начало" — всегда вернёт тебя в главное меню""", parse_mode="Markdown")
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

    await event.answer("🏠 Главное меню! "
                        "Выбери действие из кнопок ниже или нажми /help для справки",
                         reply_markup=builder.as_markup()
                         )

    await state.clear()
