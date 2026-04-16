
import db
import models
from services.for_handlers import additional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def add_task(data, id_user):
    bd = await db.Repo().create_db()
    task = models.Task(name=data["name"], deadline=data["deadline"], priority=data["priority"], note=data["note"])
    await bd.add_task(task, id_user)


async def view_tasks(id_user, param=None, key=None) -> list[list]:
    bd = await db.Repo().connect()
    task_dict = await bd.show_tasks(id_user, param,key)
    return await additional.create_output(task_dict)



async def format_output_task(user_id:int, task_id:int):
    bd = await db.Repo().connect()
    data_db = await bd.search_by_id(user_id, task_id)
    task = await additional.create_output(data_db)
    meow = (
        f"*task:* {task[0][1]}\n\n"
        f"*создано в:* {task[0][2]},\n"
        f"*выполнить до:* {task[0][3]},\n"
        f"*приоритет:* {"высокий" if task[0][4]=="high" else "средний" if task[0][4]=="medium" else "низкий"},\n"
        f"\n*подробности:* {task[0][5]},\n\n"
        f"*{"не выполнена!" if task[0][6]==0 else "выполнена!"}*")
    return meow


# for_handlers

def get_kb():
    keyboard = [
        [KeyboardButton(text="добавить задачу"),
         KeyboardButton(text="редактировать задачу")],
        [KeyboardButton(text="отметить выполнение"),
         KeyboardButton(text="удалить задачу")],
        [KeyboardButton(text="список задач"),
         KeyboardButton(text="установить напоминание")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    return reply_markup