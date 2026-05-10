# здесь будут дополнительные штуки для украшения или оформления вывода и проверки,
# использоваться они будут и в main и в basic и в optional handlers

from aiogram.utils.keyboard import InlineKeyboardBuilder

import db

async def create_db():
    bd = await db.Repo().create_tables()
    return bd


async def create_output(list_task:list[dict]) -> list[list]:

    res = []

    for task in list_task:
        res.append([
        task["id"],
        task["name"],
        task["created_at"],
        task["deadline"],
        task["priority"],
        task["note"],
        task["completed"]
    ])

    return res


async def choice_priority():
    builder = InlineKeyboardBuilder()

    builder.button(text="высокий",
                   callback_data="high")

    builder.button(text="средний",
                   callback_data="medium")

    builder.button(text="низкий",
                   callback_data="low")

    return builder.as_markup()


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

    if (31 < day or day < 0) or (0 > month or month > 12) or len(str(year)) != 4:
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


def something(text):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="что-нибудь",callback_data=text)
    return keyboard


async def try_deadline(message, state, point):
    deadline = message.text.strip()
    try:
        await check_deadline(deadline)
    except ValueError:
        await message.reply("ёклмн! Твой дедлайн должен быть не раньше сегодняшнего дня!\nПопробуй снова:")
    else:
        if await check_deadline(deadline):
            await state.update_data(deadline=message.text.strip())
            await message.reply("Дедлайн успешно установлен! Нажми что-нибудь чтобы продолжить",
                                reply_markup=something(point).as_markup())
        else:
            await message.reply("ёклмн! Твой дедлайн должен быть в формате дд.мм.гггг!\nПопробуй снова:")


async def is_task_exists(user_id, task_name:str):
    if await db.Repo().is_exist(user_id=user_id,task_name=task_name):
        return "Сорри, у тебя уже существует задача с таким именем, выбери другое!"