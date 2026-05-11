
from aiogram import Router, F, types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.for_handlers import for_main, additional
from db import Repo

router = Router()


class StatesMAIN(StatesGroup):
    name = State()
    deadline = State()
    priority = State()
    note = State()



# ниже базовые хендлеры для создания и просмотра задач


@router.message(lambda message: message.text == "добавить задачу")
@router.callback_query(F.data == "добавить задачу")
async def add_task(event: types.CallbackQuery | types.Message, state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        await event.message.answer("Придумайте название вашей задачи:")
        await event.answer()
    else:
        await event.answer("Придумайте название для вашей задачи:")
    await state.set_state(StatesMAIN.name)


@router.message(StatesMAIN.name)
async def try_save_name(message: types.Message, state: FSMContext, repo: Repo):
    res = await additional.is_task_exists(message.from_user.id, message.text, repo)
    if isinstance(res, str):
        await message.reply(res)
    else:
        await state.update_data(name=message.text.strip())
        await message.reply("Теперь укажи до какого числа нужно выполнить задачу"
                        "(дедлайн указывается в формате дд.мм.гггг)")
        await state.set_state(StatesMAIN.deadline)


@router.message(StatesMAIN.deadline)
async def try_save_deadline(message: types.Message, state: FSMContext, repo: Repo):
    try:
        await additional.try_deadline(message, state, repo)
    except ValueError:
        return

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
    await state.set_state(StatesMAIN.priority)


@router.callback_query(StatesMAIN.priority)
async def save_priority_ask_note(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.data)
    await callback.message.reply("Супер! Теперь напиши об этой задаче подробнее и мы добавим ее в календарь!")
    await callback.answer()
    await state.set_state(StatesMAIN.note)


@router.message(StatesMAIN.note)
async def save_note_getkb(message: types.Message, state:FSMContext, repo: Repo):
    await state.update_data(note=message.text.strip())
    await for_main.add_task(await state.get_data(), message.from_user.id, repo)

    reply_markup =  for_main.get_kb()

    await message.reply('Отлично, мы создали задачу! Теперь ты можешь посмотреть ее, нажав в меню "список задач"',
                        reply_markup=reply_markup)

    await state.clear()


@router.message(lambda message: message.text == "список задач")
@router.callback_query(F.data == "список задач")
async def view_tasks(event: (types.CallbackQuery | types.Message)):
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

    if isinstance(event, types.CallbackQuery):
        await event.message.answer("Выберите как отправить ваши задачи:",
                              reply_markup=builder.as_markup()
                              )
        await event.answer()
    else:
        await event.answer("Выберите как отправить ваши задачи:",
                                   reply_markup=builder.as_markup()
                                   )


@router.callback_query(F.data=="sort")
async def sort(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await for_main.view_tasks(callback.from_user.id, repo)

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
async def first_new(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await   for_main.view_tasks(
        callback.from_user.id,
        repo,
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

    builder.button(text="сначала с заканчивающимся дедлайном",callback_data="dead_desc")
    builder.button(text="с высоким приоритетом", callback_data="priority_high")
    builder.button(text="с низким приоритетом", callback_data="priority_low")
    builder.button(text="сначала с длинным описанием", callback_data="long_note")
    builder.button(text="сначала с коротким описанием", callback_data="short_note")
    builder.button(text="выполненные", callback_data="completed")
    builder.button(text="невыполненные", callback_data="no_completed")
    builder.button(text="вернуться в начало", callback_data="exit")

    builder.adjust(1)

    await callback.message.answer("Выберите как показать ваши задачи:", reply_markup=builder.as_markup())


@router.callback_query(F.data=="dead_desc")
async def dead_desc(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await for_main.view_tasks(callback.from_user.id, repo, "deadline", "ASC")

    if not array:
        await callback.message.answer("У вас пока нет задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1],callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Ваши задачи, отсортированные по времени истечения дедлайна."
                                  "Сначала самые срочные:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda bebebe: bebebe.data in ("priority_high","priority_low"))
async def priority_high(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await for_main.view_tasks(
        callback.from_user.id,
        repo,
        "priority",
        "high" if callback.data=="priority_high" else "low"
    )

    if not array:
        await callback.message.answer("У вас пока нет таких задач(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await callback.message.answer("Вот подходящие:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda f: f.data in ("long_note","short_note"))
async def long_note(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await for_main.view_tasks(
        callback.from_user.id,
        repo,
        "note",
        "DESC" if callback.data=="long_note" else "ASC"
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
async def completed(callback: CallbackQuery, repo: Repo):
    builder = InlineKeyboardBuilder()
    array = await for_main.view_tasks(
        callback.from_user.id,
        repo,
        "completed",
        "1" if callback.data == "completed" else "0"
    )

    if not array:
        await callback.message.answer("У вас пока нет задач выбранного типа(")
        await callback.answer()
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    textblock = await for_main.translate_completed(callback.data)

    await callback.message.answer(f"Ваши {textblock} задачи:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(lambda data: data.data and data.data.startswith("task-"))
async def list_tasks(callback: CallbackQuery, repo: Repo):
    """
    выводит конкретную таску
    """
    task_id = int(callback.data[5::])
    user_id = callback.from_user.id
    print(user_id)
    await callback.message.answer(f"{await for_main.format_output_task(user_id, task_id, repo)}", parse_mode="Markdown")
