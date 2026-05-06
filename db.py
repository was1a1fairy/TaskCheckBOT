import aiosqlite
from models import Task,User

class Repo:


    def __init__(self, path: str = "repo.db"):
        self.path = path
        # self.conn: Optional[aiosqlite.Connection] = None
        self.conn = None

# основные\для бд

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None


    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        # Удобно получить строки не как кортежи, а как словари (dict)
        self.conn.row_factory = aiosqlite.Row
        return self



    async def create_tables(self):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
            PRAGMA foreign_keys = ON;
        """)
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                tg_id TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                register_at TEXT NOT NULL
                ) 
            """
        )
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
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
                ) 
            """
        )
        await self.conn.commit()
        await self.close()
        return self

# добавление пользователя(регистрация)

    async def register(self, user: User, id_from_user:int):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
                INSERT INTO users
                (tg_id, email, password, register_at)
                VALUES
                (?,?,?,datetime('now'))
            """,(id_from_user,user.email,user.password))
        await self.conn.commit()
        await self.close()


    async def search_user(self, user_id:int):
        if not self.conn:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM users
                        WHERE tg_id = ?;
                        """, (user_id,))
        if not res:
            return False
        user = await res.fetchone()
        await self.close()
        return [dict(user)]


# предметные/главные


    async def add_task(self, task: Task, id_from_user:int):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
                INSERT INTO tasks
                (name, created_at, deadline, priority, note, user_id)
                VALUES
                (?,datetime('now'),?,?,?,?)
            """,(task.name,task.deadline,task.priority,task.note,id_from_user))
        await self.conn.commit()
        await self.close()


    async def edit_task(self, user_id, id_task, param_for_change, new_value):
        print(f"DB edit_task called: user_id={user_id}, id_task={id_task}, param={param_for_change}, value={new_value}")
        if not self.conn:
            await self.connect()

        print(f"__check_params result: {Repo.__check_params(param_for_change)}")
        if Repo.__check_params(param_for_change):
            cursor = await self.conn.execute(f"""
                UPDATE tasks
                SET {param_for_change} = ?
                WHERE id = ? AND user_id = ?;
                """, (new_value, id_task, user_id))
            await self.conn.commit()

            if cursor.rowcount == 0: print("no such task or user")
            print("Database updated successfully")
            await self.close()
        else:
            print("Parameter check failed")


    async def show_tasks(self, id_from_user, param_for_sort=None, sort_key=None) -> list:
        """
        имеется возможность сортировки
        !по дате:
        (asc - покажет сначала старые задачи, desc - сначала самые новые.)
        !по приоритету(1,2,3):
        (asc - с приоритетом 1(самые важные), desc - от менее важных к важным)
        !по дедлайну:
        (asc - сначала кончающийся дедлайн(самые срочные), desc - от менее срочных к срочным)
        !выполнены или нет:
        (0 - покажет только невыполненные, 1 - только выполненные)
        """

        if not self.conn:
            await self.connect()
        if not param_for_sort:
            res = await self.conn.execute("""
                SELECT * FROM tasks
                WHERE user_id = ?;
                """, (id_from_user,))
        elif Repo.__check_params(param_for_sort):
            if param_for_sort in ("completed","priority"):
                res = await self.conn.execute(f"""
                                SELECT * FROM tasks WHERE user_id = ?
                                AND {param_for_sort} = ?;
                                """, (id_from_user, sort_key))
            else:
                res = await self.conn.execute(f"""
                SELECT * FROM tasks WHERE user_id = ?
                ORDER BY {param_for_sort} {sort_key};
                """, (id_from_user,))
        else:
            await self.close()
            raise ValueError
        rows = await res.fetchall()
        await self.close()
        return [dict(row) for row in rows]


    async def delete_task(self, id_task):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
            DELETE FROM tasks WHERE id = ?;
            """, (id_task,))
        await self.conn.commit()
        await self.close()


    async def complete(self, id_task):
        if not self.conn:
            await self.connect()
        await self.conn.execute("""
                UPDATE tasks
                SET completed = 1
                WHERE id = ?;
            """, (id_task,),)
        await self.conn.commit()
        await self.close()


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


# служебные\дополнительные

    async def search_by_id(self, user_id:int, task_id:int):
        if not self.conn:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM tasks
                        WHERE user_id = ? AND id = ?;
                        """, (user_id, task_id))
        task = await res.fetchone()
        await self.close()
        return [dict(task)]



    @staticmethod
    def __check_params(param_for_change:str) -> bool:
        return param_for_change in ("name","created_at","deadline","priority","note", "completed")


    async def is_exist(self, user_id:str, task_name:str) -> bool:
        """
        проверяет есть ли у юзера уже таска с таким именем,
        которое он хочет присвоить новой
        """
        if not self.conn:
            await self.connect()
        res = await self.conn.execute("""
                SELECT * FROM tasks
                WHERE user_id = ? AND name = ?;
            """, (user_id, task_name),)
        res = await res.fetchone()
        await self.close()
        if res:
            return 1
        return 0


    async def date_now(self):
        """

        :return: дату в формате [дд, мм, гггг]
        """
        if not self.conn:
            await self.connect()
        res = await self.conn.execute("""
                SELECT date('now');
            """)
        data = await res.fetchone()
        await self.close()
        return data[0].split("-")[::-1]
