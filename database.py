#conexion de la BD
import mysql.connector

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="2118",
            database="map",
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
    except Exception as e:
        print(f"Error al conectar a MySQL: {e}")
        return None