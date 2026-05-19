from aiogram.utils.keyboard import InlineKeyboardBuilder
import db


async def create_db():
    """Создает таблицы в базе данных"""
    bd = await db.Repo().create_tables()
    return bd


async def create_output(list_task: list[dict]) -> list[list]:
    """Преобразует список задач в формат для вывода"""

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
    """Создает клавиатуру выбора приоритета"""
    builder = InlineKeyboardBuilder()

    builder.button(text="высокий",
                   callback_data="high")

    builder.button(text="средний",
                   callback_data="medium")

    builder.button(text="низкий",
                   callback_data="low")

    return builder.as_markup()


async def check_deadline(deadline: str, db: db.Repo) -> bool:
    """Проверяет корректность введения дедлайна"""
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

    if (day < 1 or day > 31) or (month < 1 or month > 12) or len(str(year)) != 4:
        return False

    now = await db.date_now()
    if now[2] > deadline[2]:
        raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
    elif now[2] == deadline[2]:
        if now[1] > deadline[1]:
            raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
        elif now[1] == deadline[1]:
            if now[0] > deadline[0]:
                raise ValueError("заданный пользователем дедлайн раньше сегодняшнего дня")
    return True


def something(text: str):
    """Создает кнопку с текстом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="что-нибудь",callback_data=text)
    return keyboard


async def try_deadline(message, state, db: db.Repo) -> None:
    """Пытается сохранить дедлайн с проверкой"""
    deadline = message.text.strip()
    try:
        await check_deadline(deadline, db)
    except ValueError:
        await message.reply("ёклмн! Твой дедлайн должен быть не раньше сегодняшнего дня!\nПопробуй снова:")
        raise ValueError
    else:
        if await check_deadline(deadline, db):
            await state.update_data(deadline=message.text.strip())
            await message.reply("Дедлайн успешно установлен!")
        else:
            await message.reply("ёклмн! Твой дедлайн должен быть в формате дд.мм.гггг!\nПопробуй снова:")
            raise ValueError


async def is_task_exists(user_id: int, task_name: str, db: db.Repo) -> str | None:
    """Проверяет существует ли задача с таким именем"""
    if await db.is_exist(user_id=user_id,task_name=task_name):
        return "Сорри, у тебя уже существует задача с таким именем, выбери другое!"