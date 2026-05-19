import re
from models import User
from db import Repo
from email_validator import validate_email, EmailNotValidError
from check_password import Check


async def check_username(username: str, repo: Repo) -> bool:
    """Проверяет валидность username"""
    if re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
        existing = await repo.search_username(username)
        if not existing:
            return True
        else:
            return False
    return False

async def check_email(email: str) -> bool:
    """Проверяет валидность email"""
    try:
        validate_email(email)
    except EmailNotValidError:
        return False
    return True


async def check_password(password: str) -> bool:
    """Проверяет валидность пароля"""
    res = Check().password(password, result_type="list", numbers=1, symbols=1, max_length=64)
    if res[0]:
        return True
    return False



async def register(user_data: dict, tg_id: int, repo: Repo) -> None:
    """Регистрирует нового пользователя"""
    user = User(username=user_data["username"],tg_id=tg_id,email=user_data["email"],password=user_data["password"])
    await repo.register(user)