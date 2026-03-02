#modelos
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re
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

class LoginRequest(BaseModel):
    email_user: EmailStr
    pass_user: str

class RegisterRequest(BaseModel):
    name_user: str
    email_user: EmailStr
    pass_user: str
    matricula_user: int
    id_rol: int 

    @field_validator("pass_user")
    @classmethod
    def validate_password(cls, v):

        # 1. Longitud mínima
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        # 2. Límite bcrypt
        if len(v) > 72:
            raise ValueError("La contraseña no puede tener más de 72 caracteres")

        # 3. Al menos un número
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        # 4. Al menos un caracter especial
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]]", v):
            raise ValueError("La contraseña debe contener al menos un caracter especial")

        return v


class UserResponse(BaseModel):
    id_user: int
    name_user: str
    email_user: str
    matricula_user: Optional[int]
    rol: str
    id_rol: int

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None