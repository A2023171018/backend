from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UsuarioResponse(BaseModel):
    id_user: int
    name_user: str
    email_user: str
    matricula_user: Optional[int] = None
    id_rol: int
    rol: str
    division: Optional[str] = None
    planta: Optional[str] = None
    edificio: Optional[str] = None

class UsuarioUpdate(BaseModel):
    name_user: Optional[str] = None
    email_user: Optional[str] = None
    matricula_user: Optional[int] = None
    id_rol: Optional[int] = None

class RegisterProfesor(BaseModel):
    name_user: str
    email_user: str
    pass_user: str
    matricula_user: int
    id_rol: int = 3
    id_division: Optional[int] = None
    planta_profe: Optional[str] = None
    id_building: Optional[int] = None

# ============================
# 📋 GET ALL USUARIOS
# ============================
@router.get("/usuarios", response_model=list[UsuarioResponse])
async def get_usuarios():
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id_user, u.name_user, u.email_user, u.matricula_user,
               u.id_rol, r.name_rol AS rol,
               d.name_div AS division,
               p.planta_profe AS planta,
               e.name_building AS edificio
        FROM usuarios u
        JOIN rol r ON u.id_rol = r.id_rol
        LEFT JOIN profesor p ON p.nombre_profe = u.name_user AND u.id_rol = 3
        LEFT JOIN divisiones d ON p.id_division = d.id_div
        LEFT JOIN edificios e ON p.id_building = e.id_building
        ORDER BY u.id_user ASC
    """)
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    return usuarios

# ============================
# ✏️ UPDATE USUARIO
# ============================
@router.put("/usuarios/{id_user}")
async def update_usuario(id_user: int, data: UsuarioUpdate):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = db.cursor()
    fields = []
    values = []
    if data.name_user is not None:
        fields.append("name_user = %s")
        values.append(data.name_user)
    if data.email_user is not None:
        fields.append("email_user = %s")
        values.append(data.email_user)
    if data.matricula_user is not None:
        fields.append("matricula_user = %s")
        values.append(data.matricula_user)
    if data.id_rol is not None:
        fields.append("id_rol = %s")
        values.append(data.id_rol)
    if not fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    values.append(id_user)
    cursor.execute(f"UPDATE usuarios SET {', '.join(fields)} WHERE id_user = %s", values)
    db.commit()
    cursor.close()
    db.close()
    return {"success": True, "message": "Usuario actualizado correctamente"}

# ============================
# 🗑️ DELETE USUARIO
# ============================
@router.delete("/usuarios/{id_user}")
async def delete_usuario(id_user: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = db.cursor(dictionary=True)

    # Verificar si el usuario existe y obtener su rol y nombre
    cursor.execute("SELECT id_rol, name_user FROM usuarios WHERE id_user = %s", (id_user,))
    usuario = cursor.fetchone()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si es profesor (id_rol = 3), eliminarlo también de la tabla profesor
    if usuario["id_rol"] == 3:
        cursor.execute("DELETE FROM profesor WHERE nombre_profe = %s", (usuario["name_user"],))
        db.commit()

    cursor.execute("DELETE FROM usuarios WHERE id_user = %s", (id_user,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True, "message": "Usuario eliminado correctamente"}

# ============================
# 🔄 TOGGLE ROL
# ============================
@router.patch("/usuarios/{id_user}/toggle-rol")
async def toggle_rol(id_user: int):
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_rol FROM usuarios WHERE id_user = %s", (id_user,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    nuevo_rol = 2 if user["id_rol"] == 1 else 1
    cursor.execute("UPDATE usuarios SET id_rol = %s WHERE id_user = %s", (nuevo_rol, id_user))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True, "nuevo_rol": nuevo_rol}

# ============================
# ➕ REGISTER PROFESOR
# ============================
@router.post("/register-profesor")
async def register_profesor(data: RegisterProfesor):
    from security import hash_password
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Error de conexión")
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id_user FROM usuarios WHERE email_user = %s", (data.email_user,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Correo ya registrado")

    try:
        hashed = hash_password(data.pass_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cursor.execute("""
        INSERT INTO usuarios (name_user, email_user, pass_user, matricula_user, id_rol)
        VALUES (%s, %s, %s, %s, 3)
    """, (data.name_user, data.email_user, hashed, data.matricula_user))
    db.commit()

    cursor.execute("""
        INSERT INTO profesor (nombre_profe, id_division, planta_profe, id_building)
        VALUES (%s, %s, %s, %s)
    """, (data.name_user, data.id_division, data.planta_profe, data.id_building))
    db.commit()

    cursor.close()
    db.close()
    return {"success": True, "message": "Profesor registrado correctamente"}

# ============================
# 📋 GET DIVISIONES
# ============================
@router.get("/divisiones")
async def get_divisiones():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_div, name_div FROM divisiones ORDER BY id_div ASC")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

# ============================
# 📋 GET EDIFICIOS LIST
# ============================
@router.get("/edificios-list")
async def get_edificios_list():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_building, name_building FROM edificios ORDER BY id_building ASC")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data