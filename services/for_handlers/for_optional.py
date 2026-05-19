from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Repo
from services.for_handlers import additional


async def inline():
    """Создает клавиатуру выбора параметра для изменения"""
    builder=InlineKeyboardBuilder()

    builder.button(text="имя",callback_data="edit_name")
    builder.button(text="дедлайн", callback_data="edit_deadline")
    builder.button(text="приоритет", callback_data="edit_priority")
    builder.button(text="описание", callback_data="edit_note")

    builder.adjust(2)
    return builder.as_markup()


async def edit_task(data: dict, user_id: int, repo: Repo) -> None:
    """Редактирует задачу"""
    for key in data:
        if key != "id" and data[key]:
            await repo.edit_task(user_id, data["id"], key, data[key])


async def view_tasks(id_user: int, repo: Repo, param: str = None, key: str = None) -> list[list]:
    """Показывает задачи пользователя"""
    task_dict = await repo.show_tasks(id_user, param,key)
    return await additional.create_output(task_dict)

async def delete_task(id_task: int, repo: Repo) -> None:
    """Удаляет задачу"""
    await repo.delete_task(id_task)


async def complete_task(id_task: int, repo: Repo) -> None:
    """Отмечает задачу как выполненную"""
    await repo.complete(id_task)