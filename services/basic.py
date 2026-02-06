import db
import models

database = db.Repo()
database.create_db()


async def add_task(data, id_user):
    task = models.Task(name=data["name"], deadline=data["deadline"], priority=data["priority"], note=data["note"])
    await database.add_task(task, id_user)


async def add_task():
    pass

async def view_tasks(user_id, param_for_sort, key_sort):
    pass