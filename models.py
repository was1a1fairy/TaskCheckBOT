from dataclasses import dataclass


@dataclass
class Task:
    """Модель задачи"""
    name: str
    deadline: str
    priority: str
    note: str
    completed: bool = 0
    id: int = None

    def __str__(self) -> str:
        return f"{self.name, self.deadline, self.priority, self.note, self.completed}"


@dataclass
class User:
    """Модель пользователя"""
    tg_id: str
    is_registered: bool = None
    username: str = None
    email: str = None
    password: str = None
    id: int = None

    def __str__(self) -> str:
        return f"{self.username, self.tg_id, self.email, self.password}"