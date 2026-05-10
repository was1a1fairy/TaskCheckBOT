import db



async def check_username(username):
    if await db.Repo().search_username(username):
        return 1
    return 0


async def check_password(password, username):
    if await db.Repo().check_password(password,username):
        return 1
    return 0


async def login(user_data, tg_id):
    await db.Repo().log_tg_id(tg_id, user_data['username'])