from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

router = APIRouter()

class EdificioCreate(BaseModel):
    name_building: str
    code_building: Optional[str] = None
    imagen_url: Optional[str] = None
    lat_building: float
    lon_building: float
    id_div: Optional[int] = None

class EdificioUpdate(BaseModel):
    name_building: Optional[str] = None
    code_building: Optional[str] = None
    imagen_url: Optional[str] = None
    lat_building: Optional[float] = None
    lon_building: Optional[float] = None
    id_div: Optional[int] = None

@router.get("/edificios")
async def get_edificios():
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_building, e.name_building, e.code_building,
               e.imagen_url, e.lat_building, e.lon_building,
               e.id_div, d.name_div
        FROM edificios e
        LEFT JOIN divisiones d ON e.id_div = d.id_div
        ORDER BY e.id_building ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    for row in data:
        for key in ["lat_building", "lon_building"]:
            if isinstance(row[key], Decimal):
                row[key] = float(row[key])
    return data

@router.post("/edificios")
async def create_edificio(data: EdificioCreate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO edificios (name_building, code_building, imagen_url, lat_building, lon_building, id_div)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data.name_building, data.code_building, data.imagen_url,
          data.lat_building, data.lon_building, data.id_div))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"success": True, "id_building": new_id}

@router.put("/edificios/{id_building}")
async def update_edificio(id_building: int, data: EdificioUpdate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    fields, values = [], []
    if data.name_building is not None:
        fields.append("name_building = %s"); values.append(data.name_building)
    if data.code_building is not None:
        fields.append("code_building = %s"); values.append(data.code_building)
    if data.imagen_url is not None:
        fields.append("imagen_url = %s"); values.append(data.imagen_url)
    if data.lat_building is not None:
        fields.append("lat_building = %s"); values.append(data.lat_building)
    if data.lon_building is not None:
        fields.append("lon_building = %s"); values.append(data.lon_building)
    if data.id_div is not None:
        fields.append("id_div = %s"); values.append(data.id_div)
    if not fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    values.append(id_building)
    cursor.execute(f"UPDATE edificios SET {', '.join(fields)} WHERE id_building = %s", values)
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@router.delete("/edificios/{id_building}")
async def delete_edificio(id_building: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    cursor.execute("DELETE FROM edificios WHERE id_building = %s", (id_building,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}