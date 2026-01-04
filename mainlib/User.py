from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    password: str
    post: str
    account: str
    vk: str
    disciplinary_actions: str
    note: str
