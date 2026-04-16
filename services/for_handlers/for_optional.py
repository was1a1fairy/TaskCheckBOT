from aiogram.utils.keyboard import InlineKeyboardBuilder
from . import additional
import db


async def inline():
    builder=InlineKeyboardBuilder()

    builder.button(text="имя",callback_data="edit_name")
    builder.button(text="дедлайн", callback_data="edit_deadline")
    builder.button(text="приоритет", callback_data="edit_priority")
    builder.button(text="описание", callback_data="edit_note")

    builder.adjust(2)
    return builder.as_markup()


async def edit_task(data:dict, user_id):
    for key in data:
        if key.value and key!="id":
            await db.Repo().edit_task(user_id,data["id"],key,key.value)


async def view_tasks(id_user, param=None, key=None) -> list[list]:
    bd = await db.Repo().connect()
    task_dict = await bd.show_tasks(id_user, param,key)
    return await additional.create_output(task_dict)