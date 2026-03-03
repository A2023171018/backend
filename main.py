from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.models import LoginRequest, RegisterRequest, LoginResponse, UserResponse
from db_supabase import get_supabase_client
from eventos_router import router as eventos_router
from usuarios_router import router as usuarios_router
from dashboard_router import router as dashboard_router
from edificios_router import router as edificios_router
from divisiones_router import router as divisiones_router

from app.utils.security import (
    verify_password,
    hash_password,
    validate_password
)

app = FastAPI()

# ============================
# 🚀 STARTUP EVENT - Probar conexión
# ============================
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("🚀 Iniciando servidor FastAPI...")
    print("="*50)
    try:
        supabase = get_supabase_client()
        # Hacer una consulta simple para verificar conexión
        supabase.table("usuarios").select("id_user", count="exact").limit(1).execute()
        print("✅ Servidor iniciado correctamente")
        print("📍 Documentación: http://localhost:8000/docs")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {str(e)}")
        print("⚠️  Verifica tu archivo .env")
        print("="*50 + "\n")

app.include_router(eventos_router)
app.include_router(usuarios_router)
app.include_router(dashboard_router)
app.include_router(edificios_router)
app.include_router(divisiones_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# 🔑 LOGIN
# ============================
@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    try:
        supabase = get_supabase_client()
        
        # Buscar usuario con rol
        response = supabase.table("usuarios").select("""
            id_user, name_user, email_user, pass_user,
            matricula_user, id_rol,
            rol!inner(name_rol)
        """).eq("email_user", credentials.email_user).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user = response.data[0]
        
        if not verify_password(credentials.pass_user, user["pass_user"]):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        return LoginResponse(
            success=True,
            message="Login exitoso",
            user=UserResponse(
                id_user=user["id_user"],
                name_user=user["name_user"],
                email_user=user["email_user"],
                matricula_user=user["matricula_user"],
                id_rol=user["id_rol"],
                rol=user["rol"]["name_rol"] if isinstance(user.get("rol"), dict) else ""
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 📝 REGISTER
# ============================
@app.post("/register")
async def register(user_data: RegisterRequest):
    try:
        supabase = get_supabase_client()
        
        # Verificar si el correo ya existe
        check = supabase.table("usuarios").select("id_user").eq("email_user", user_data.email_user).execute()
        if check.data:
            raise HTTPException(status_code=409, detail="Correo ya registrado")
        
        # Hash de la contraseña
        try:
            hashed_password = hash_password(user_data.pass_user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Insertar usuario
        supabase.table("usuarios").insert({
            "name_user": user_data.name_user,
            "email_user": user_data.email_user,
            "pass_user": hashed_password,
            "matricula_user": user_data.matricula_user,
            "id_rol": user_data.id_rol
        }).execute()
        
        return {"success": True, "message": "Usuario registrado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 🚀 Run local
# ============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)