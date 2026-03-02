from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class DivisionCreate(BaseModel):
    name_div: str

class DivisionUpdate(BaseModel):
    name_div: Optional[str] = None

# ============================
# 📋 GET ALL DIVISIONES
# ============================
@router.get("/divisiones-all")
async def get_divisiones_all():
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.id_div, d.name_div,
               COUNT(p.id_profe) AS total_profesores,
               COUNT(e.id_building) AS total_edificios
        FROM divisiones d
        LEFT JOIN profesor p ON p.id_division = d.id_div
        LEFT JOIN edificios e ON e.id_div = d.id_div
        GROUP BY d.id_div, d.name_div
        ORDER BY d.id_div ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

# ============================
# ➕ CREATE DIVISION
# ============================
@router.post("/divisiones")
async def create_division(data: DivisionCreate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    cursor.execute("INSERT INTO divisiones (name_div) VALUES (%s)", (data.name_div,))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"success": True, "id_div": new_id}

# ============================
# ✏️ UPDATE DIVISION
# ============================
@router.put("/divisiones/{id_div}")
async def update_division(id_div: int, data: DivisionUpdate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor()
    if not data.name_div:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    cursor.execute("UPDATE divisiones SET name_div = %s WHERE id_div = %s", (data.name_div, id_div))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ============================
# 🗑️ DELETE DIVISION
# ============================
@router.delete("/divisiones/{id_div}")
async def delete_division(id_div: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)

    # Verificar si tiene profesores o edificios asociados
    cursor.execute("SELECT COUNT(*) AS total FROM profesor WHERE id_division = %s", (id_div,))
    if cursor.fetchone()["total"] > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene profesores asociados")

    cursor.execute("SELECT COUNT(*) AS total FROM edificios WHERE id_div = %s", (id_div,))
    if cursor.fetchone()["total"] > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene edificios asociados")

    cursor.execute("DELETE FROM divisiones WHERE id_div = %s", (id_div,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}