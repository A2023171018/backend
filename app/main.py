from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.models import LoginRequest, RegisterRequest, LoginResponse, UserResponse, ResetPasswordRequest, OAuthSyncRequest
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
# � OAUTH SYNC
# ============================
@app.post("/auth/oauth/sync")
async def oauth_sync(data: OAuthSyncRequest):
    """
    Sincroniza un usuario autenticado con OAuth (Google, etc.) con la tabla usuarios.
    Si el usuario no existe, lo crea. Si existe, retorna sus datos.
    """
    try:
        print(f"[OAuth Sync] Recibiendo solicitud para usuario: {data.email_user}")
        print(f"[OAuth Sync] ID: {data.id_user}, Provider: {data.provider}")
        
        supabase = get_supabase_client()
        
        # Verificar si el usuario ya existe en la tabla usuarios
        print(f"[OAuth Sync] Verificando si usuario existe en tabla usuarios...")
        result = supabase.table("usuarios").select("*").eq("id_user", data.id_user).execute()
        print(f"[OAuth Sync] Resultado de búsqueda: {len(result.data) if result.data else 0} usuarios encontrados")
        
        if result.data and len(result.data) > 0:
            # Usuario ya existe, obtener sus datos con el nombre del rol
            user_data = result.data[0]
            
            # Obtener nombre del rol
            rol_result = supabase.table("rol").select("name_rol").eq("id_rol", user_data["id_rol"]).execute()
            rol_name = rol_result.data[0]["name_rol"] if rol_result.data else "Usuario"
            
            return {
                "success": True,
                "message": "Usuario autenticado correctamente",
                "user": {
                    "id_user": user_data["id_user"],
                    "name_user": user_data["name_user"],
                    "email_user": user_data["email_user"],
                    "matricula_user": user_data.get("matricula_user", 0),
                    "id_rol": user_data["id_rol"],
                    "rol": rol_name
                }
            }
        else:
            # Usuario no existe, crear uno nuevo
            # Por defecto, los usuarios de OAuth son "Usuario" (id_rol = 2)
            print(f"[OAuth Sync] Usuario no existe, creando nuevo usuario...")
            new_user = {
                "id_user": data.id_user,  # UUID de Supabase Auth
                "name_user": data.name_user,
                "email_user": data.email_user,
                "pass_user": None,  # NULL para usuarios OAuth
                "matricula_user": 0,  # Los usuarios OAuth no tienen matrícula inicialmente
                "id_rol": 2  # Rol "Usuario" por defecto
            }
            
            print(f"[OAuth Sync] Datos a insertar: {new_user}")
            insert_result = supabase.table("usuarios").insert(new_user).execute()
            print(f"[OAuth Sync] Resultado de inserción: {insert_result.data}")
            
            if not insert_result.data:
                error_msg = f"Error al crear usuario en la base de datos. Resultado: {insert_result}"
                print(f"[OAuth Sync] ERROR: {error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Obtener nombre del rol
            rol_result = supabase.table("rol").select("name_rol").eq("id_rol", 2).execute()
            rol_name = rol_result.data[0]["name_rol"] if rol_result.data else "Usuario"
            
            return {
                "success": True,
                "message": "Usuario creado y autenticado correctamente",
                "user": {
                    "id_user": data.id_user,
                    "name_user": data.name_user,
                    "email_user": data.email_user,
                    "matricula_user": 0,
                    "id_rol": 2,
                    "rol": rol_name
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en sincronización OAuth: {str(e)}")


# ============================
# �🚀 Run local
# ============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)