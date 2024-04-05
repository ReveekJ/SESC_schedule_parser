from pydantic import BaseModel


# TODO: сделать более продвинутую модель
class User(BaseModel):
    id: int
    role: str
    sub_info: str
    lang: str
