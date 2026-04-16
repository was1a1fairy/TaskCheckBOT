from aiogram import Router, F, types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.for_handlers import for_optional, additional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery


router3 = Router()

class StatesOPTIONAL(StatesGroup):
    id = State()
    name = State()
    deadline = State()
    priority = State()
    note = State()


@router3.message(lambda message: message.text == "редактировать задачу")
async def edit_task(message: types.Message):
    builder = InlineKeyboardBuilder()
    array = await for_optional.view_tasks(message.from_user.id)

    if not array:
        await message.answer("У вас пока нет задач(")
        return

    for task in array:
        builder.button(text=task[1], callback_data=f"task-{task[0]}")

    builder.adjust(1)

    await message.answer("Выберите задачу для изменения:", reply_markup=builder.as_markup())


@router3.callback_query(lambda data: data.data and data.data.startswith("task-"))
async def chose_changes(callback: CallbackQuery, state:FSMContext):
    task_id = int(callback.data[5::])
    await state.update_data(id=task_id)
    await callback.message.answer("Изменить:",reply_markup= await for_optional.inline())


@router3.callback_query(F.data=="edit_name")
async def edit_name(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.name)
    await callback.message.answer("Введите новое имя:")


@router3.message(StatesOPTIONAL.name)
async def try_save_name(message: types.Message, state: FSMContext):
    res = await additional.is_task_exists(message.from_user.id, message.text)
    if isinstance(res, str):
        await message.reply(res)
    else:
        await state.update_data(name=message.text.strip())
        await message.reply("Имя добавлено успешно! Нажми что-нибудь чтобы продолжить",
                            reply_markup=additional.something("something").as_markup())


@router3.callback_query(F.data=="edit_deadline")
async def edit_deadline(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.deadline)
    await callback.message.answer("Введите новый дедлайн:")


@router3.message(StatesOPTIONAL.deadline)
async def try_save_deadline(message: types.Message, state: FSMContext):
    await additional.try_deadline(message,state)


@router3.callback_query(F.data=="edit_priority")
async def edit_priority(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.priority)
    await callback.message.answer("Выберите новый приоритет:",
                                  reply_markup=await additional.choice_priority())


@router3.callback_query(F.data=="edit_note")
async def edit_note(callback:types.CallbackQuery, state:FSMContext):
    await state.set_state(StatesOPTIONAL.note)
    await callback.message.answer("Введите новое описание:")


@router3.message(StatesOPTIONAL.__all_states__)
@router3.callback_query(lambda f: f.data in ("True","something"))
async def editing_complete(event:types.Message|types.CallbackQuery, state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        event = event.message

    user_input = event.text

    current_state = (await state.get_state()).split(':')[-1]

    await state.update_data({current_state:user_input})
    await for_optional.edit_task(await state.get_data(), event.from_user.id)
    await state.clear()
    await event.answer("Данные успешно обновлены!")


@router3.message(lambda message: True)
async def handler(message: types.Message):
    await message.reply("Я не умею распознавать сообщения, воспользуйся пожалуйста командой или меню!\n/help")