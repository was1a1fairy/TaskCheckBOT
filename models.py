from dataclasses import dataclass


@dataclass
class Task:

    name: str
    deadline: str
    priority: str
    note: str