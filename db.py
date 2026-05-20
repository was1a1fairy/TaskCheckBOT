
import aiosqlite
from models import Task, User


class Repo:
    """Репозиторий для работы с базой данных"""

    def __init__(self, path: str = "repo.db") -> None:
        self.path = path
        self.conn = None

    async def close(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn:
            await self.conn.close()
            self.conn = None


    async def connect(self) -> 'Repo':
        """Устанавливает соединение с базой данных и создает таблицы"""
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.create_tables()
        return self



    async def create_tables(self) -> 'Repo':
        """Создает таблицы в базе данных"""
        await self.conn.execute("""
            PRAGMA foreign_keys = ON;
        """)

        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                email TEXT,
                password TEXT,
                is_registered BOOLEAN NOT NULL DEFAULT 0,
                register_at TEXT NOT NULL
            )
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
                user_tg_id INTEGER NOT NULL
                )
            """)

        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_tg_id INTEGER NOT NULL,
                remind_days INTEGER NOT NULL,
                sent INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (user_tg_id) REFERENCES users(tg_id)
                )
            """)

        await self.conn.commit()
        return self

    async def register(self, user: User) -> None:
        """Регистрирует нового пользователя или обновляет существующего"""
        if self.conn is None:
            await self.connect()
        await self.conn.execute("""
            INSERT OR REPLACE INTO users
            (tg_id, username, email, password, is_registered, register_at)
            VALUES (?, ?, ?, ?, 1, datetime('now'))
        """, (user.tg_id, user.username, user.email, user.password))
        await self.conn.commit()


    async def add_unregistered_user(self, user_id: int) -> None:
        """Добавляет незарегистрированного пользователя"""
        if self.conn is None:
            await self.connect()
        await self.conn.execute("""
                INSERT INTO users
                (tg_id, is_registered, register_at)
                VALUES
                (?,0,datetime('now'))
            """,(user_id,))
        await self.conn.commit()


    async def search_user(self, user_id: int) -> list[dict] | bool:
        """Ищет пользователя по telegram id"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM users
                        WHERE tg_id = ?;
                        """, (user_id,))
        user = await res.fetchone()
        if not user:
            return False
        return [dict(user)]

    async def search_username(self, username: str) -> list[dict] | bool:
        """Ищет пользователя по username"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM users
                        WHERE username = ?;
                        """, (username,))
        user = await res.fetchone()
        if not user:
            return False
        return [dict(user)]


    async def search_email(self, email: str) -> list[dict] | bool:
        """Ищет пользователя по email"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM users
                        WHERE email = ?;
                        """, (email,))
        user = await res.fetchone()
        if not user:
            return False
        return [dict(user)]


    async def log_tg_id(self, tg_id: int, username: str) -> None:
        """Привязывает telegram id к username"""
        if self.conn is None:
            await self.connect()
        await self.conn.execute("""
            UPDATE users
            SET tg_id = ?
            WHERE username = ?;
        """, (tg_id, username))

        await self.conn.commit()


    async def check_password(self, password: str, username: str) -> bool:
        """Проверяет пароль пользователя"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM users
                        WHERE username = ?
                        AND password = ?;
                        """, (username,password))
        user = await res.fetchone()
        if not user:
            return False
        return True


    async def add_task(self, task: Task, id_from_user: int) -> None:
        """Добавляет новую задачу"""
        if self.conn is None:
            await self.connect()
        try:
            await self.conn.execute("""
                    INSERT INTO tasks
                    (name, created_at, deadline, priority, note, user_tg_id)
                    VALUES
                    (?,datetime('now'),?,?,?,?)
                """, (task.name, task.deadline, task.priority, task.note, id_from_user))
            await self.conn.commit()
        except Exception as e:
            print(f"Error adding task: {e}")
            raise


    async def edit_task(self, user_id: int, id_task: int, param_for_change: str, new_value: str) -> None:
        """Редактирует задачу"""
        if self.conn is None:
            await self.connect()
        if self.__check_params(param_for_change):
            await self.conn.execute(f"""
                UPDATE tasks
                SET {param_for_change} = ?
                WHERE id = ? AND user_tg_id = ?;
                """, (new_value, id_task, user_id))
            await self.conn.commit()


    async def show_tasks(self, id_from_user: int, param_for_sort: str = None, sort_key: str = None) -> list[dict]:
        """
        Показывает задачи с возможностью сортировки по дате, приоритету, дедлайну или статусу выполнения
        """
        if self.conn is None:
            await self.connect()
        if not param_for_sort:
            res = await self.conn.execute("""
                SELECT * FROM tasks
                WHERE user_tg_id = ?;
                """, (id_from_user,))
        elif Repo.__check_params(param_for_sort):
            if param_for_sort in ("completed","priority"):
                res = await self.conn.execute(f"""
                                SELECT * FROM tasks WHERE user_tg_id = ?
                                AND {param_for_sort} = ?;
                                """, (id_from_user, sort_key))
            else:
                res = await self.conn.execute(f"""
                SELECT * FROM tasks WHERE user_tg_id = ?
                ORDER BY {param_for_sort} {sort_key};
                """, (id_from_user,))
        else:
            raise ValueError
        rows = await res.fetchall()
        return [dict(row) for row in rows]


    async def delete_task(self, id_task: int) -> None:
        """Удаляет задачу"""
        if self.conn is None:
            await self.connect()
        try:
            await self.conn.execute("""
                DELETE FROM tasks WHERE id = ?;
                """, (id_task,))
            await self.conn.commit()
        except Exception as e:
            print(f"Error deleting task: {e}")
            raise


    async def complete(self, id_task: int) -> None:
        """Отмечает задачу как выполненную"""
        if self.conn is None:
            await self.connect()
        try:
            await self.conn.execute("""
                    UPDATE tasks
                    SET completed = 1
                    WHERE id = ?;
                """, (id_task,),)
            await self.conn.commit()
        except Exception as e:
            print(f"Error completing task: {e}")
            raise

    async def expired_tasks(self) -> list:
        """Выдает задачи с истекающим дедлайном"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
            SELECT user_tg_id, name
            FROM tasks
            WHERE date(deadline) <= date('now', '+1 day') AND completed = 0
        """)
        data = await res.fetchall()
        return data

    async def add_reminder(self, task_id: int, user_tg_id: int, remind_days: int) -> None:
        """Добавляет напоминание для задачи"""
        if self.conn is None:
            await self.connect()
        await self.conn.execute("""
            INSERT INTO reminders (task_id, user_tg_id, remind_days, sent)
            VALUES (?, ?, ?, 0)
        """, (task_id, user_tg_id, remind_days))
        await self.conn.commit()

    async def get_pending_reminders(self) -> list:
        """Получает задачи с индивидуальными напоминаниями, которые нужно отправить"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
            SELECT r.user_tg_id, t.name
            FROM reminders r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.sent = 0 AND date(t.deadline) <= date('now', '+' || r.remind_days || ' day') AND t.completed = 0
        """)
        data = await res.fetchall()
        return data

    async def mark_reminders_sent(self, user_tg_id: int, task_name: str) -> None:
        """Отмечает напоминания как отправленные для задачи"""
        if self.conn is None:
            await self.connect()
        await self.conn.execute("""
            UPDATE reminders SET sent = 1
            WHERE user_tg_id = ? AND task_id IN (SELECT id FROM tasks WHERE name = ?)
        """, (user_tg_id, task_name))
        await self.conn.commit()


    async def search_by_id(self, user_id: int, task_id: int) -> list[dict]:
        """Ищет задачу по id"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                        SELECT * FROM tasks
                        WHERE user_tg_id = ? AND id = ?;
                        """, (user_id, task_id))
        task = await res.fetchone()
        return [dict(task)]



    @staticmethod
    def __check_params(param_for_change:str) -> bool:
        return param_for_change in ("name","created_at","deadline","priority","note", "completed")


    async def is_exist(self, user_id: str, task_name: str) -> bool:
        """Проверяет есть ли у пользователя задача с таким именем"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                SELECT * FROM tasks
                WHERE user_tg_id = ? AND name = ?;
            """, (user_id, task_name),)
        res = await res.fetchone()
        return bool(res)


    async def date_now(self) -> list[str]:
        """Возвращает текущую дату в формате [дд, мм, гггг]"""
        if self.conn is None:
            await self.connect()
        res = await self.conn.execute("""
                SELECT date('now');
            """)
        data = await res.fetchone()
        return data[0].split("-")[::-1]

    async def get_user_analytics(self, user_id: int) -> dict:
        """Возвращает аналитику пользователя: статистику задач"""
        if self.conn is None:
            await self.connect()
        
        # Общее количество задач
        res = await self.conn.execute("""
            SELECT COUNT(*) FROM tasks WHERE user_tg_id = ?;
        """, (user_id,))
        total_tasks = (await res.fetchone())[0]
        
        # Выполненные задачи
        res = await self.conn.execute("""
            SELECT COUNT(*) FROM tasks WHERE user_tg_id = ? AND completed = 1;
        """, (user_id,))
        completed_tasks = (await res.fetchone())[0]
        
        # Задачи по приоритетам
        res = await self.conn.execute("""
            SELECT priority, COUNT(*) FROM tasks WHERE user_tg_id = ? GROUP BY priority;
        """, (user_id,))
        priority_data = await res.fetchall()
        priority_stats = {row[0]: row[1] for row in priority_data}
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "priority_stats": priority_stats
        }
