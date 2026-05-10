from aiogram import Router, F, types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.for_handlers import for_optional, additional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery


router = Router()

class StatesOPTIONAL(StatesGroup):
    id = State()
    name = State()
    deadline = State()
    priority = State()
    note = State()


# edit task:

@router.message(lambda message: message.text == "редактировать задачу")
async def edit_task(message: types.Message):
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для изменения:", reply_markup=builder.as_markup())


@router.callback_query(lambda data: data.data and data.data.startswith("task"))
async def chose_changes(callback: CallbackQuery, state:FSMContext):
    task_id = int(callback.data[4::])
    await state.update_data(id=task_id)
    await callback.message.answer("Изменить:",reply_markup= await for_optional.inline())


@router.callback_query(F.data=="edit_name")
async def edit_name(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.name)
    await callback.message.answer("Введите новое имя:")


@router.message(StatesOPTIONAL.name)
async def try_save_name(message: types.Message, state: FSMContext):
    print(message.text, message.from_user.id)
    res = await additional.is_task_exists(message.from_user.id, message.text)
    if isinstance(res, str):
        await message.reply(res)
    else:
        await state.update_data(name=message.text.strip())
        await message.reply("Имя добавлено успешно! Нажми что-нибудь чтобы продолжить",
                            reply_markup=additional.something("something").as_markup())


@router.callback_query(F.data=="edit_deadline")
async def edit_deadline(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.deadline)
    await callback.message.answer("Введите новый дедлайн:")


@router.message(StatesOPTIONAL.deadline)
async def try_save_deadline(message: types.Message, state: FSMContext):
    print(message.text, message.from_user.id)
    await additional.try_deadline(message,state,"something")


@router.callback_query(F.data=="edit_priority")
async def edit_priority(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.priority)
    await callback.message.answer("Выберите новый приоритет:",
                                  reply_markup=await additional.choice_priority())


@router.callback_query(StatesOPTIONAL.priority)
@router.callback_query(lambda bebebe: bebebe.data in ("high", "medium", "low"))
async def save_priority(callback: types.CallbackQuery, state:FSMContext):
    await state.update_data(priority=callback.data)
    await editing_complete(callback,state)
    await callback.answer()


@router.callback_query(F.data=="edit_note")
async def edit_note(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.note)
    await callback.message.answer("Введите новое описание:")


@router.message(StatesOPTIONAL.note)
async def save_priority(message: types.Message, state:FSMContext):
    await state.update_data(note=message.text)
    await editing_complete(message,state)


# @router.message()
@router.callback_query(lambda f: f.data == "something")
async def editing_complete(event:types.Message|types.CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if isinstance(event, types.CallbackQuery):
        event = event.message

    await for_optional.edit_task(await state.get_data(), user_id)
    await state.clear()
    await event.answer("Данные успешно обновлены!")


# delete task:

@router.message(lambda message: message.text == "удалить задачу")
async def delete_task(message: types.Message):
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"del{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для удаления:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del"))
async def delete(callback:types.CallbackQuery):
    task_id = int(callback.data[3:])
    await for_optional.delete_task(task_id)
    await callback.message.edit_text("Задача была удалена!")


# set complete status for task

@router.message(lambda message: message.text == "отметить выполнение")
async def set_status_complete(message: types.Message):
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"set{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для отметки выполнения:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("set"))
async def complete(callback:types.CallbackQuery):
    task_id = int(callback.data[3:])
    await for_optional.complete_task(task_id)
    await callback.message.edit_text("Вы выполнили задачу!")
