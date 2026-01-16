from dataclasses import dataclass


@dataclass
class Task:

    id: int
    name: str
    created_at: str
    deadline: str
    priority: str
    note: str
    complited:bool