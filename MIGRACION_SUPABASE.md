# 🚀 Guía de Migración a Supabase

## ✅ Cambios Completados

Tu proyecto ha sido migrado para usar **Supabase** con el cliente oficial de Python. Los cambios incluyen:

- ✅ Configuración simplificada (solo 2 credenciales)
- ✅ Todos los routers actualizados
- ✅ Sintaxis moderna del cliente Supabase
- ✅ Manejo automático de conexiones

---

## 📋 Pasos para Completar la Migración

### 1️⃣ Obtén tus Credenciales de Supabase

1. Ve a [supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto (o crea uno nuevo)
3. Ve a **Settings** → **API**
4. Copia estos dos valores:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

### 2️⃣ Crea el Archivo `.env`

En la carpeta `/backend`, crea un archivo llamado `.env` y pega tus credenciales:

```env
SUPABASE_URL=https://xxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tu-anon-key-aqui
```

### 3️⃣ Instala las Dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install supabase python-dotenv fastapi uvicorn pydantic[email] bcrypt passlib
```

### 4️⃣ Migra tu Base de Datos MySQL a Supabase

#### Opción A: Migración Manual

1. Exporta tu base de datos MySQL:

```bash
mysqldump -u root -p map > backup.sql
```

2. En Supabase, ve a **Database** → **SQL Editor**
3. Ejecuta tu esquema (CREATE TABLE statements)
4. Importa los datos

#### Opción B: Usar Herramientas de Migración

- Usa [pgloader](https://pgloader.io/) para migrar de MySQL a PostgreSQL
- Supabase tiene guías en: https://supabase.com/docs/guides/migrations

### 5️⃣ Configura las Foreign Keys en Supabase

Para que las relaciones funcionen (los JOINs que usa el código), asegúrate de que en Supabase estén configuradas las foreign keys:

```sql
-- Ejemplo para la tabla usuarios
ALTER TABLE usuarios
ADD CONSTRAINT fk_usuarios_rol
FOREIGN KEY (id_rol) REFERENCES rol(id_rol);

-- Ejemplo para eventos
ALTER TABLE eventos
ADD CONSTRAINT fk_eventos_edificios
FOREIGN KEY (id_building) REFERENCES edificios(id_building);

-- Etc...
```

### 6️⃣ Prueba la Conexión

```bash
python main.py
```

Si todo está configurado correctamente, el servidor debería iniciar en `http://localhost:8000`

---

## 🗑️ Archivos que Puedes Eliminar (Opcional)

Una vez que todo funcione, puedes eliminar:

- `database.py` (ya no se usa)
- Cualquier backup de MySQL

---

## 📊 Diferencias Clave

### Antes (MySQL):

```python
db = get_db_connection()
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM eventos")
eventos = cursor.fetchall()
cursor.close()
db.close()
```

### Ahora (Supabase):

```python
supabase = get_supabase_client()
response = supabase.table("eventos").select("*").execute()
eventos = response.data
```

---

## 🆘 Resolución de Problemas

### Error: "Faltan SUPABASE_URL o SUPABASE_KEY"

- Verifica que el archivo `.env` esté en la carpeta correcta
- Asegúrate de que las variables estén escritas exactamente como `SUPABASE_URL` y `SUPABASE_KEY`

### Error: "relation does not exist"

- La tabla no existe en Supabase
- Necesitas migrar tu esquema de base de datos

### Error de Foreign Key

- Configura las relaciones en Supabase para que los JOINs funcionen
- Ve a **Database** → **Table Editor** → selecciona una tabla → **Add foreign key**

---

## 📚 Recursos

- [Documentación Supabase Python](https://supabase.com/docs/reference/python)
- [Migración de MySQL a PostgreSQL](https://supabase.com/docs/guides/migrations/mysql)
- [API Reference](https://supabase.com/docs/reference/python/select)

---

¿Necesitas ayuda? Los cambios están completos, solo necesitas:

1. Obtener tus 2 credenciales de Supabase
2. Crear el archivo `.env`
3. Migrar tu base de datos
4. ¡Listo! 🎉
