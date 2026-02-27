from certifi import contents

import db
import models
from services import additional


async def add_task(data, id_user):
    bd = await db.Repo().create_db()
    task = models.Task(name=data["name"], deadline=data["deadline"], priority=data["priority"], note=data["note"])
    await bd.add_task(task, id_user)


async def view_tasks(id_user, param=None, key=None) -> list[list]:
    bd = await db.Repo().create_db()
    task_dict = await bd.show_tasks(id_user, param,key)
    return await additional.create_output(task_dict)


async def format_output_task(user_id:int, task_id:int):
    bd = await db.Repo().create_db()
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


async def check_deadline(deadline) -> bool:
    """
    проверяет корректность введения дедлайна
    :param deadline: дд.мм.гггг
    :return: bool
    """
    if "\\" in deadline:
        deadline = deadline.split("\\")
    elif "/" in deadline:
        deadline = deadline.split("/")
    elif "." in deadline:
        deadline = deadline.split(".")
    else:
        return False

    if len(deadline) != 3:
        return False

    day = int(deadline[0])
    month = int(deadline[1])
    year = int(deadline[2])

    if (31 < day < 0) or (0 > month > 12) or year < 2026:
        return False

    now = await db.Repo().date_now()
    if now[2] > deadline[2]:
        raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
    elif now[2] == deadline[2]:
        if now[1] > deadline[1]:
            raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
        elif now[1] == deadline[1]:
            if now[0] > deadline[0]:
                raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
    return True


