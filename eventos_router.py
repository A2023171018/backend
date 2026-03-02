from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class EventoCreate(BaseModel):
    name_event: str
    id_building: Optional[int] = None
    timedate_event: Optional[datetime] = None
    id_profe: Optional[int] = None
    id_user: Optional[int] = None

class EventoUpdate(BaseModel):
    name_event: Optional[str] = None
    id_building: Optional[int] = None
    timedate_event: Optional[datetime] = None
    id_profe: Optional[int] = None
    id_user: Optional[int] = None

@router.get("/eventos")
async def get_eventos():
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_event, name_event, id_building, timedate_event, status_event, id_profe, id_user FROM eventos ORDER BY id_event ASC")
    eventos = cursor.fetchall()
    cursor.close()
    db.close()
    for e in eventos:
        if e["timedate_event"]:
            e["timedate_event"] = str(e["timedate_event"])
    return eventos

@router.post("/eventos")
async def create_evento(data: EventoCreate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO eventos (name_event, id_building, timedate_event, status_event, id_profe, id_user)
        VALUES (%s, %s, %s, 1, %s, %s)
    """, (data.name_event, data.id_building, data.timedate_event, data.id_profe, data.id_user))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"success": True, "id_event": new_id}

@router.put("/eventos/{id_event}")
async def update_evento(id_event: int, data: EventoUpdate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    fields, values = [], []
    if data.name_event is not None:
        fields.append("name_event = %s"); values.append(data.name_event)
    if data.id_building is not None:
        fields.append("id_building = %s"); values.append(data.id_building)
    if data.timedate_event is not None:
        fields.append("timedate_event = %s"); values.append(data.timedate_event)
    if data.id_profe is not None:
        fields.append("id_profe = %s"); values.append(data.id_profe)
    if data.id_user is not None:
        fields.append("id_user = %s"); values.append(data.id_user)
    if not fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    values.append(id_event)
    cursor.execute(f"UPDATE eventos SET {', '.join(fields)} WHERE id_event = %s", values)
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@router.patch("/eventos/{id_event}/toggle-status")
async def toggle_status_evento(id_event: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT status_event FROM eventos WHERE id_event = %s", (id_event,))
    evento = cursor.fetchone()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    nuevo_status = 0 if evento["status_event"] == 1 else 1
    cursor.execute("UPDATE eventos SET status_event = %s WHERE id_event = %s", (nuevo_status, id_event))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True, "nuevo_status": nuevo_status}

@router.delete("/eventos/{id_event}")
async def delete_evento(id_event: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    cursor.execute("DELETE FROM eventos WHERE id_event = %s", (id_event,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@router.get("/edificios")
async def get_edificios():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_building, name_building FROM edificios ORDER BY id_building ASC")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

@router.get("/profesores")
async def get_profesores():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_profe, nombre_profe FROM profesor ORDER BY id_profe ASC")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data