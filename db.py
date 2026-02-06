import aiosqlite
from typing import Optional
from models import Task

class Repo:


    def __init__(self, path: str = "repo.db"):
        self.path = path
        # self.conn: Optional[aiosqlite.Connection] = None
        self.conn = None


    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None


    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        # Удобно получить строки не как кортежи, а как словари (dict)
        self.conn.row_factory = aiosqlite.Row


    async def create_db(self):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
            PRAGMA foreign_keys = ON;
        """)
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                deadline TEXT,
                priority TEXT DEFAULT 'low',
                note TEXT,
                completed INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL
                ) 
            """
        )
        await self.conn.commit()
        await self.close()


    async def add_task(self, task: Task, id_from_user:int):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
                INSERT INTO tasks
                (name, created_at, deadline, priority, note, user_id)
                VALUES
                (?,datetime('now'),?,?,?,?)
            """,(task.name,task.deadline,task.priority,task.note,id_from_user),)
        await self.conn.commit()
        await self.close()


    def __check_params(self, param_for_change):
        return (param_for_change in ("name","created_at","deadline","priority","note"))

    async def edit_task(self, id_task, param_for_change, new_value):
        if not self.conn:
            await self.connect()

        if self.__check_params(param_for_change):
            await self.conn.execute(f"""
                UPDATE tasks
                SET {param_for_change} = ?
                WHERE id = ?;
                """, (new_value, id_task))
            await self.conn.commit()
            await self.close()


    async def delete_task(self, id_task):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
            DELETE FROM tasks WHERE id = ?;
            """, (id_task,))
        await self.conn.commit()
        await self.close()


    async def task_is_complete(self, id_task):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
                UPDATE tasks
                SET completed = 1
                WHERE id = ?;
            """, (id_task,),)
        await self.conn.commit()
        await self.close()


    async def show_tasks(self, id_from_user, param_for_sort=None,sort_key=None) -> list:
        """
        имеется возможность сортировки
        !по дате:
        (asc - покажет сначала старые задачи, desc - сначала самые новые.)
        !по приоритету(1,2,3):
        (asc - с приоритетом 1(самые важные), desc - от менее важных к важным)
        !по дедлайну:
        (asc - сначала кончающийся дедлайн(самые срочные), desc - от менее срочных к срочным)
        !выполнены или нет:
        (asc - сначала невыполненные, desc - сначала выполненные)
        """

        if not self.conn:
            await self.connect()
        if not param_for_sort:
            res = await self.conn.execute("""
                SELECT * FROM tasks
                WHERE user_id = ?;
                """, (id_from_user,))
        elif self.__check_params(param_for_sort):
            res = await self.conn.execute(f"""
                SELECT * FROM tasks WHERE user_id = ?
                ORDER BY {param_for_sort} {sort_key};
                """, (id_from_user,))
        else:
            await self.close()
            return
        rows = await res.fetchall()
        await self.close()
        return [dict(row) for row in rows]


    async def search_task(self, key_word:str) -> Task:
        if not self.conn:
            await self.connect()
        res_task = await self.conn.execute("""
            ....покажет таски где
             в названии или в описании конкретное слово
        """)
        await self.close()
        return res_task


    async def show_by_date(self, date: str):
        if not self.conn:
            await self.connect()
        res_task = await self.conn.execute("""
            ....покажет таски за конкретную дату
        """)
        await self.close()
        return res_task