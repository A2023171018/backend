from fastapi import APIRouter, HTTPException
from app.config import get_supabase_client
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
    try:
        supabase = get_supabase_client()
        response = supabase.table("eventos").select("id_event, name_event, id_building, timedate_event, status_event, id_profe, id_user").order("id_event").execute()
        eventos = response.data
        for e in eventos:
            if e.get("timedate_event"):
                e["timedate_event"] = str(e["timedate_event"])
        return eventos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/eventos")
async def create_evento(data: EventoCreate):
    try:
        supabase = get_supabase_client()
        evento_data = {
            "name_event": data.name_event,
            "id_building": data.id_building,
            "timedate_event": data.timedate_event.isoformat() if data.timedate_event else None,
            "status_event": 1,
            "id_profe": data.id_profe,
            "id_user": data.id_user
        }
        response = supabase.table("eventos").insert(evento_data).execute()
        return {"success": True, "id_event": response.data[0]["id_event"] if response.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/eventos/{id_event}")
async def update_evento(id_event: int, data: EventoUpdate):
    try:
        supabase = get_supabase_client()
        update_data = {}
        if data.name_event is not None:
            update_data["name_event"] = data.name_event
        if data.id_building is not None:
            update_data["id_building"] = data.id_building
        if data.timedate_event is not None:
            update_data["timedate_event"] = data.timedate_event.isoformat()
        if data.id_profe is not None:
            update_data["id_profe"] = data.id_profe
        if data.id_user is not None:
            update_data["id_user"] = data.id_user
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        supabase.table("eventos").update(update_data).eq("id_event", id_event).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.patch("/eventos/{id_event}/toggle-status")
async def toggle_status_evento(id_event: int):
    try:
        supabase = get_supabase_client()
        response = supabase.table("eventos").select("status_event").eq("id_event", id_event).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        evento = response.data[0]
        nuevo_status = 0 if evento["status_event"] == 1 else 1
        supabase.table("eventos").update({"status_event": nuevo_status}).eq("id_event", id_event).execute()
        return {"success": True, "nuevo_status": nuevo_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/eventos/{id_event}")
async def delete_evento(id_event: int):
    try:
        supabase = get_supabase_client()
        supabase.table("eventos").delete().eq("id_event", id_event).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/profesores")
async def get_profesores():
    try:
        supabase = get_supabase_client()
        response = supabase.table("profesor").select("id_profe, nombre_profe").order("id_profe").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")