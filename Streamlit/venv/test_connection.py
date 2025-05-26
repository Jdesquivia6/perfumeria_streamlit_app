import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_db_connection():
    try:
        connection = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME')
        )
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print(f"✅ Conexión exitosa. La hora actual del servidor es: {result[0]}")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == '__main__':
    test_db_connection()
