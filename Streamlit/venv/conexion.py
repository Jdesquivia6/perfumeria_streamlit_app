import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv('run_results_scraping_perfumeria.csv')

try:
    connection = psycopg2.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME')
    )
    cursor = connection.cursor()
    print("✅ Conexión exitosa a Supabase")

    insert_query = """
        INSERT INTO perfumes_scraping (
            producto_name, producto_url, producto_especificaciones, producto_especificaciones_url,
            producto_vendido_por, producto_vendido_por_url, producto_precio_descuento, producto_precio_descuento_url,
            producto_precio_con_oferta, producto_precio_con_oferta_url, producto_precio_sin_oferta, producto_precio_sin_oferta_url,
            producto_promocion_blackdays, producto_promocion_blackdays_url, producto_referencias, producto_referencias_url,
            producto_descuento, producto_descuento_url, producto_tiempo_llegada, producto_tiempo_llegada_url,
            producto_envios_gratis, producto_envios_gratis_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """

    records_inserted = 0

    for _, row in df.iterrows():
        values = (
            row.get('producto_name'),
            row.get('producto_url'),
            row.get('producto_especificaciones'),
            row.get('producto_especificaciones_url'),
            row.get('producto_vendido_por'),
            row.get('producto_vendido_por_url'),
            row.get('producto_precio_descuento'),
            row.get('producto_precio_descuento_url'),
            row.get('producto_precio_con_oferta'),
            row.get('producto_precio_con_oferta_url'),
            row.get('producto_precio_sin_oferta'),
            row.get('producto_precio_sin_oferta_url'),
            row.get('producto_promocion_blackdays'),
            row.get('producto_promocion_blackdays_url'),
            row.get('producto_referencias'),
            row.get('producto_referencias_url'),
            row.get('producto_descuento'),
            row.get('producto_descuento_url'),
            row.get('producto_tiempo_llegada'),
            row.get('producto_tiempo_llegada_url'),
            row.get('producto_envios_gratis'),
            row.get('producto_envios_gratis_url')
        )
        cursor.execute(insert_query, values)
        records_inserted += 1

    connection.commit()
    print(f"Se insertaron {records_inserted} registros correctamente.")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"Error al insertar en Supabase: {e}")
