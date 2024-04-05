from typing import Optional

from pydantic import BaseModel


class ChangesType(BaseModel):
    id: Optional[int] = None
    type: str
    second: str
    weekday: str
    schedule: dict
