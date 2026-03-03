# Conexión a Supabase usando el cliente oficial
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Variable para controlar si ya se mostró el log de conexión
_connection_logged = False

def get_supabase_client() -> Client:
    """
    Retorna el cliente de Supabase configurado.
    Solo necesitas SUPABASE_URL y SUPABASE_KEY en tu archivo .env
    """
    global _connection_logged
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Faltan SUPABASE_URL o SUPABASE_KEY en el archivo .env")
        raise ValueError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en el archivo .env")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Mostrar log solo la primera vez
        if not _connection_logged:
            print("✅ Conexión a Supabase establecida correctamente")
            print(f"📡 URL: {SUPABASE_URL}")
            _connection_logged = True
        
        return client
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {str(e)}")
        raise
  