from gc import callbacks
from operator import index

from aiogram import filters, Router, F, types
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery, KeyboardButton
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
import services.basic
import db

router = Router()

class States(StatesGroup):
    """
    ne_deadline = not enough deadline, используется перед проверкой корректности дедлайна
    """
    name = State()
    ne_deadline = State()
    deadline = State()
    priority = State()
    note = State()

class StateView(StatesGroup):
    pass


@router.message(filters.Command("start"))
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


@router.callback_query(F.data=="help")
async def helpp(callback: CallbackQuery):
    await callback.message.reply(f"""Тебе нужна помощь?
    Давай объясню что я умею и покажу как пользоваться моими командами!\n
    Нажми добавить задачу, последовательно выбирай настройки
    Добавляй нужное количество задач и отслеживай их через "список задач" в меню!""")


@router.callback_query(F.data=="exit")
async def exitt(callback:CallbackQuery):
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

# ниже базовые хендлеры для создания и просмотра задач

@router.callback_query(F.data=="добавить задачу")
async def add_task(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.answer("Придумайте название вашей задаче:")
    await callback.answer()
    await state.set_state(States.name)


@router.message(States.name)
async def save_name_ask_deadline(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text.strip())
    await message.reply("Супер! Теперь укажи до какого числа нужно выполнить задачу"
                        "(дедлайн указывается в формате дд.мм.гггг)")
    await state.set_state(States.ne_deadline)


@router.message(States.ne_deadline)
async def try_save_deadline(message: types.Message, state: FSMContext):
    deadline = message.text.strip()
    try:
        await services.basic.check_deadline(deadline)
    except ValueError:
        await message.reply("ёклмн! Твой дедлайн должен быть не раньше сегодняшнего дня!\nПопробуй снова:")
    else:
        if await services.basic.check_deadline(deadline):
            await state.update_data(deadline=message.text.strip())
            await state.set_state(States.deadline)
            await message.reply("Дедлайн успешно установлен! Нажми что-нибудь чтобы продолжить")
        else:
            await message.reply("ёклмн! Твой дедлайн должен быть в формате дд.мм.гггг!\nПопробуй снова:")


@router.message(States.deadline)
async def ask_priority(message: types.Message, state:FSMContext):

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


@router.callback_query(lambda bebebe: bebebe.data in ("high", "medium", "low"))
async def save_priority_ask_note(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.data)
    await callback.message.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await callback.answer()
    await state.set_state(States.note)


@router.message(States.note)
async def save_note_getkb(message: types.Message, state:FSMContext):
    await state.update_data(note=message.text.strip())
    await services.basic.add_task(await state.get_data(), message.from_user.id)

    reply_markup = services.basic.get_kb()

    await message.reply('Отлично, мы создали задачу! Теперь ты можешь посмотреть ее, нажав в меню "список задач"',
                        reply_markup=reply_markup)

    await state.clear()



@router.callback_query(F.data=="список задач")
async def view_tasks(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.button(text="по умолчанию",
                   callback_data="sort")

    builder.button(text="сначала новые задачи",
                   callback_data="first_new")

    builder.button(text="сначала старые задачи",
                   callback_data="first_old")

    builder.button(text="выбрать параметр для сортировки",
                   callback_data="chose_param")

    builder.button(text="вернуться в начало",
                   callback_data="exit")

    builder.adjust(1)

    await callback.message.answer("Выберите как отправить ваши задачи:",
                          reply_markup=builder.as_markup()
                          )

    await callback.answer()


@router.callback_query(F.data=="sort")
async def sort(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(callback.from_user.id)

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda bebebe: bebebe.data in ("first_new","first_old"))
async def first_new(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(
        callback.from_user.id,
        "created_at",
        "DESC" if callback.data=="first_new" else "ASC"
    )

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data=="chose_param")
async def chose_param(callback:CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.button(text="заканчивающимся дедлайном",callback_data="dead_desc")
    builder.button(text="высоким приоритетом", callback_data="priority_high")
    builder.button(text="низким приоритетом", callback_data="priority_low")
    builder.button(text="самым длинным описанием", callback_data="long_note")
    builder.button(text="самым коротким описанием", callback_data="short_note")
    builder.button(text="выполненные", callback_data="completed")
    builder.button(text="невыполненные", callback_data="no_completed")
    builder.button(text="вернуться в начало", callback_data="exit")

    builder.adjust(1)

    await callback.message.answer("Показать сначала задачи с:", reply_markup=builder.as_markup())


@router.callback_query(F.data=="dead_desc")
async def dead_desc(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(callback.from_user.id, "deadline", "DESC")

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1],callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda bebebe: bebebe.data in ("priority_high","priority_low"))
async def priority_high(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(
        callback.from_user.id,
        "priority",
        "DESC" if callback.data=="priority_high" else "ASC"
    )

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda f: f.data in ("long_note","short_note"))
async def long_note(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(
        callback.from_user.id,
        "note",
        "ASC" if callback.data=="long_note" else "DESC"
    )

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda f: f.data in ("completed","no_completed"))
async def completed(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    array = await services.basic.view_tasks(
        callback.from_user.id,
        "completed",
        "DESC" if "completed" else "ASC"
    )

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda data: data.data and data.data.startswith("task-"))
async def list_tasks(callback: CallbackQuery):
    task_id = int(callback.data[5::])
    user_id = callback.from_user.id
    print(user_id)
    await callback.message.answer(f"{await services.basic.format_output_task(user_id, task_id)}", parse_mode="Markdown")








# других хендлеров не будет
@router.message(lambda message: True)
async def handler(message: types.Message):
    await message.reply("Я не умею распознавать сообщения, воспользуйся пожалуйста командой или меню!\n/help")