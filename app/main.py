from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.models import LoginRequest, RegisterRequest, LoginResponse, UserResponse, ResetPasswordRequest
from app.config import get_supabase_client
from app.services.auth_service import AuthService
from app.routers.eventos_router import router as eventos_router
from app.routers.usuarios_router import router as usuarios_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.edificios_router import router as edificios_router
from app.routers.divisiones_router import router as divisiones_router
from app.routers.asistencias_router import router as asistencias_router
from app.routers.horarios_router import router as horarios_router

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
app.include_router(asistencias_router)
app.include_router(horarios_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# 🔑 LOGIN con Supabase Auth
# ============================
@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    try:
        result = await AuthService.sign_in(
            email=credentials.email_user,
            password=credentials.pass_user
        )
        
        user_data = result["user_data"]
        
        return LoginResponse(
            success=True,
            message="Login exitoso",
            user=UserResponse(
                id_user=user_data["id_user"],
                name_user=user_data["name_user"],
                email_user=user_data["email_user"],
                matricula_user=user_data.get("matricula_user"),
                id_rol=user_data["id_rol"],
                rol=user_data["rol"]
            ),
            session={
                "access_token": result["session"].access_token,
                "refresh_token": result["session"].refresh_token,
                "expires_at": result["session"].expires_at
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 📝 REGISTER con Supabase Auth
# ============================
@app.post("/register")
async def register(user_data: RegisterRequest):
    try:
        # Validar contraseña antes de enviar a Supabase
        from app.utils.security import validate_password
        try:
            validate_password(user_data.pass_user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Registrar con Supabase Auth
        result = await AuthService.sign_up(
            email=user_data.email_user,
            password=user_data.pass_user,
            metadata={
                "name_user": user_data.name_user,
                "matricula_user": user_data.matricula_user,
                "id_rol": user_data.id_rol
            }
        )
        
        return {
            "success": True,
            "message": "Usuario registrado correctamente. Revisa tu email para verificar tu cuenta."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 🔄 RESET PASSWORD
# ============================
@app.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    try:
        result = await AuthService.reset_password(data.email)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 🚪 LOGOUT
# ============================
@app.post("/logout")
async def logout():
    try:
        result = await AuthService.sign_out("")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================
# 🚀 Run local
# ============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)