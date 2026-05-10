from models import User
import db
from email_validator import validate_email, EmailNotValidError
from check_password import Check

async def check_username(username) -> bool:
    if Check().password(username, min_length=6, max_length=20):
        if not await db.Repo().search_username(username):
            return 1
    return 0

async def check_email(email) -> bool:
    try:
        validate_email(email)
    except EmailNotValidError:
        return 0
    return 1


async def check_password(password) -> bool:
    res=Check().password(password, result_type="list", numbers=1, symbols=1, max_length=64)
    print(res)
    if res[0]:
        return 0
    return 1



async def register(user_data, tg_id):
    user = User(username=user_data["username"],tg_id=tg_id,email=user_data["email"],password=user_data["password"])
    if await db.Repo().search_user(tg_id):
        return "Вы уже зарегистрированы с этого телеграм аккаунта, сорян(("
    await db.Repo().register(user)