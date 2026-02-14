from dataclasses import dataclass


@dataclass
class Task:

    name: str
    deadline: str
    priority: str
    note: str
    completed:bool=0
    id:int=None

    def __str__(self):
        return f"{self.name,self.deadline,self.priority,self.note,self.completed}"