from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventoBase(BaseModel):
    name_event: str
    id_building: Optional[int] = None
    timedate_event: Optional[datetime] = None
    status_event: Optional[int] = 1
    id_profe: Optional[int] = None
    id_user: Optional[int] = None

##lol
class EventoCreate(EventoBase):
    pass


class EventoResponse(EventoBase):
    id_event: int

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email_user: EmailStr
    pass_user: str