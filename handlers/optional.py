from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.for_handlers import for_optional, additional
from db import Repo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery

router = Router()

class StatesOPTIONAL(StatesGroup):
    id = State()
    name = State()
    deadline = State()
    priority = State()
    note = State()


@router.message(lambda message: message.text == "редактировать задачу")
async def edit_task(message: types.Message, repo: Repo) -> None:
    """Показывает список задач для редактирования"""
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id, repo)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для изменения:", reply_markup=builder.as_markup())


@router.callback_query(lambda data: data.data and data.data.startswith("task"))
async def chose_changes(callback: CallbackQuery, state: FSMContext) -> None:
    """Показывает меню выбора параметра для редактирования"""
    task_id = int(callback.data[4::])
    await state.update_data(id=task_id)
    await callback.message.answer("Изменить:",reply_markup= await for_optional.inline())


@router.callback_query(F.data=="edit_name")
async def edit_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрашивает новое название задачи"""
    await state.set_state(StatesOPTIONAL.name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите новое имя:")


@router.message(StatesOPTIONAL.name)
async def try_save_name(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет и сохраняет новое название задачи"""
    res = await additional.is_task_exists(message.from_user.id, message.text, repo)
    if isinstance(res, str):
        await message.reply(res)
    else:
        await state.update_data(name=message.text.strip())
        await editing_complete(message,state, repo)


@router.callback_query(F.data=="edit_deadline")
async def edit_deadline(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрашивает новый дедлайн задачи"""
    await state.set_state(StatesOPTIONAL.deadline)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите новый дедлайн:")


@router.message(StatesOPTIONAL.deadline)
async def try_save_deadline(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Проверяет и сохраняет новый дедлайн задачи"""
    try:
        await additional.try_deadline(message,state,repo)
    except ValueError:
        return
    await editing_complete(message, state, repo)


@router.callback_query(F.data=="edit_priority")
async def edit_priority(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрашивает новый приоритет задачи"""
    await state.set_state(StatesOPTIONAL.priority)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите новый приоритет:",
                                  reply_markup=await additional.choice_priority())


@router.callback_query(StatesOPTIONAL.priority)
async def save_priority(callback: types.CallbackQuery, state: FSMContext, repo: Repo) -> None:
    """Сохраняет новый приоритет задачи"""
    await state.update_data(priority=callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)
    await editing_complete(callback,state, repo)
    await callback.answer()


@router.callback_query(F.data=="edit_note")
async def edit_note(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрашивает новое описание задачи"""
    await state.set_state(StatesOPTIONAL.note)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите новое описание:")


@router.message(StatesOPTIONAL.note)
async def save_note(message: types.Message, state: FSMContext, repo: Repo) -> None:
    """Сохраняет новое описание задачи"""
    await state.update_data(note=message.text)
    await editing_complete(message,state, repo)


async def editing_complete(event: types.Message | types.CallbackQuery, state: FSMContext, repo: Repo) -> None:
    """Завершает редактирование задачи"""
    user_id = event.from_user.id
    if isinstance(event, types.CallbackQuery):
        event = event.message

    await for_optional.edit_task(await state.get_data(), user_id, repo)
    await state.clear()
    await event.answer("Данные успешно обновлены!")


@router.message(lambda message: message.text == "удалить задачу")
async def delete_task(message: types.Message, repo: Repo) -> None:
    """Показывает список задач для удаления"""
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id, repo)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"del{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для удаления:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del"))
async def delete(callback: types.CallbackQuery, repo: Repo) -> None:
    """Удаляет выбранную задачу"""
    task_id = int(callback.data[3:])
    await for_optional.delete_task(task_id, repo)
    await callback.message.edit_text("Задача была удалена!")


@router.message(lambda message: message.text == "отметить выполнение")
async def set_status_complete(message: types.Message, repo: Repo) -> None:
    """Показывает список задач для отметки выполнения"""
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id, repo)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"set{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для отметки выполнения:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("set"))
async def complete(callback: types.CallbackQuery, repo: Repo) -> None:
    """Отмечает задачу как выполненную"""
    task_id = int(callback.data[3:])
    await for_optional.complete_task(task_id, repo)
    await callback.message.edit_text("Вы выполнили задачу!")


@router.message(lambda message: message.text == "установить напоминание")
async def set_reminder(message: types.Message, repo: Repo) -> None:
    """Показывает список задач для установки напоминания"""
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id, repo)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"remind{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для установки напоминания:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("remind"))
async def set_(callback: types.CallbackQuery) -> None:
    """Показывает выбор времени для напоминания"""
    task_id = int(callback.data[6:])
    builder = InlineKeyboardBuilder()
    builder.button(text="1 день", callback_data=f"1_{task_id}_day")
    builder.button(text="2 дня", callback_data=f"2_{task_id}_day")
    builder.button(text="3 дня", callback_data=f"3_{task_id}_day")
    builder.button(text="неделю", callback_data=f"7_{task_id}_day")
    builder.adjust(1)

    await callback.message.answer("Напомнить через...", reply_markup=builder.as_markup())


@router.callback_query(F.data.endswith("_day"))
async def set_reminder_time(callback: types.CallbackQuery, repo: Repo) -> None:
    """Устанавливает напоминание на выбранное время"""
    user_id = callback.from_user.id
    task_id = int(callback.data.split('_')[1])
    days = int(callback.data.split('_')[0])
    
    task = await repo.search_by_id(user_id, task_id)
    if not task:
        await callback.message.answer("Задача не найдена")
        return
    
    task_name = task[0]['name']
    
    await repo.add_reminder(task_id, user_id, days)
    
    await callback.message.answer(f"Напоминание установлено на {days} дн. для задачи '{task_name}'")

