from db import Repo


async def check_username(username: str, repo: Repo) -> int:
    """Проверяет существует ли username"""
    if await repo.search_username(username):
        return 1
    return 0


async def check_password(password: str, username: str, repo: Repo) -> int:
    """Проверяет правильность пароля"""
    if await repo.check_password(password,username):
        return 1
    return 0


async def login(user_data: dict, tg_id: int, repo: Repo) -> None:
    """Привязывает telegram id к username"""
    await repo.log_tg_id(tg_id, user_data['username'])