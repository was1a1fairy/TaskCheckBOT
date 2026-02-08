import db
import models


async def add_task(data, id_user):
    bd = await db.Repo().create_db()
    print(data)
    task = models.Task(name=data["name"], deadline=data["deadline"], priority=data["priority"], note=data["note"])
    await bd.add_task(task, id_user)


async def view_tasks(user_id, param_for_sort, key_sort):
    pass