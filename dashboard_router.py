from fastapi import APIRouter
from database import get_db_connection
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard/stats")
async def get_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    now = datetime.now()
    inicio_semana = now - timedelta(days=now.weekday())
    inicio_mes = now.replace(day=1)
    inicio_dia = now.replace(hour=0, minute=0, second=0)

    # Total usuarios
    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    total_usuarios = cursor.fetchone()["total"]

    # Total eventos
    cursor.execute("SELECT COUNT(*) as total FROM eventos")
    total_eventos = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return {
        "total_usuarios": total_usuarios,
        "total_eventos": total_eventos,
    }

@router.get("/dashboard/grafica")
async def get_grafica(periodo: str = "semana"):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    now = datetime.now()

    if periodo == "dia":
        # Últimas 24 horas por hora
        cursor.execute("""
            SELECT DATE_FORMAT(timedate_event, '%H:00') as label, COUNT(*) as eventos
            FROM eventos
            WHERE timedate_event >= %s
            GROUP BY label ORDER BY label ASC
        """, (now - timedelta(hours=24),))
        eventos = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%H:00') as label, COUNT(*) as usuarios
            FROM usuarios
            WHERE created_at >= %s
            GROUP BY label ORDER BY label ASC
        """, (now - timedelta(hours=24),))
        usuarios = cursor.fetchall()

    elif periodo == "semana":
        # Últimos 7 días
        cursor.execute("""
            SELECT DATE_FORMAT(timedate_event, '%a') as label, COUNT(*) as eventos
            FROM eventos
            WHERE timedate_event >= %s
            GROUP BY label, DATE(timedate_event) ORDER BY DATE(timedate_event) ASC
        """, (now - timedelta(days=7),))
        eventos = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%a') as label, COUNT(*) as usuarios
            FROM usuarios
            WHERE created_at >= %s
            GROUP BY label, DATE(created_at) ORDER BY DATE(created_at) ASC
        """, (now - timedelta(days=7),))
        usuarios = cursor.fetchall()

    else:  # mes
        # Últimos 30 días por día
        cursor.execute("""
            SELECT DATE_FORMAT(timedate_event, '%d/%m') as label, COUNT(*) as eventos
            FROM eventos
            WHERE timedate_event >= %s
            GROUP BY label, DATE(timedate_event) ORDER BY DATE(timedate_event) ASC
        """, (now - timedelta(days=30),))
        eventos = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%d/%m') as label, COUNT(*) as usuarios
            FROM usuarios
            WHERE created_at >= %s
            GROUP BY label, DATE(created_at) ORDER BY DATE(created_at) ASC
        """, (now - timedelta(days=30),))
        usuarios = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "eventos": eventos,
        "usuarios": usuarios,
    }

@router.get("/dashboard/reporte")
async def get_reporte():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.name_user, u.email_user, u.matricula_user, r.name_rol AS rol
        FROM usuarios u JOIN rol r ON u.id_rol = r.id_rol
        ORDER BY u.id_user ASC
    """)
    usuarios = cursor.fetchall()

    cursor.execute("""
        SELECT e.name_event, ed.name_building, e.timedate_event,
               p.nombre_profe, e.status_event
        FROM eventos e
        LEFT JOIN edificios ed ON e.id_building = ed.id_building
        LEFT JOIN profesor p ON e.id_profe = p.id_profe
        ORDER BY e.timedate_event DESC
    """)
    eventos = cursor.fetchall()

    cursor.close()
    db.close()

    return {"usuarios": usuarios, "eventos": eventos}