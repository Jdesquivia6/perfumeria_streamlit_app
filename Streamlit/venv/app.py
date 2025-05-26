import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
import os
import re
from dotenv import load_dotenv

st.set_page_config(layout="wide")
st.title("Análisis Exploratorio de Datos - Perfumería (Supabase/PostgreSQL)")

load_dotenv()

try:
    connection = psycopg2.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME')
    )
    cursor = connection.cursor()
    st.success("✅ Conexión exitosa a Supabase")
except Exception as e:
    st.error(f"❌ Error al conectarse a Supabase: {e}")


try:
    query = "SELECT * FROM perfumes_scraping;"
    data = pd.read_sql_query(query, connection)

    data = data.convert_dtypes().infer_objects()

    st.success("Datos cargados exitosamente desde Supabase.")

    cols_to_drop = [col for col in data.columns if "url" in col.lower()]
    data = data.drop(columns=cols_to_drop)

except Exception as e:
    st.error(f"❌ Error al leer y filtrar los datos: {e}")


def limpiar_precio(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).lower()
    valor = re.sub(r'[^\d.,]', '', valor)
    valor = valor.replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except:
        return None

precio_vars = [
    "producto_precio_descuento",
    "producto_precio_con_oferta",
    "producto_precio_sin_oferta"
]

for col in precio_vars:
    if col in data.columns:
        data[col] = data[col].apply(limpiar_precio)

# Variables cuantitativas y cualitativas
cuant_vars = data.select_dtypes(include=["number"]).columns.tolist()
cuali_vars = data.select_dtypes(include=["object", "string", "category", "boolean"]).columns.tolist()


# 1. Estructura y Vista Inicial del Dataset
with st.expander("1. Estructura y Vista Inicial del Dataset", expanded=True):
    st.subheader("Nombres de columnas y Tipos de Datos")
    st.write(data.dtypes)

    st.subheader("Primeros 5 Registros")
    st.dataframe(data.head())


# 2. Muestra Personalizada del Dataset

with st.expander("2. Muestra Personalizada del Dataset"):
    n = st.slider("Seleccione cuántas filas desea mostrar:", 5, 50, 10)
    st.dataframe(data.sample(n))

    cols = st.multiselect("Seleccione columnas para visualizar:", data.columns.tolist())
    if cols:
        st.dataframe(data[cols].head())



# 4. Análisis Bivariado
with st.expander("4. Análisis Bivariado"):
    if len(cuali_vars) > 0 and len(cuant_vars) > 0:
        var_cuali = cuali_vars[0]
        var_cuant = cuant_vars[0]
        st.markdown(f"### Relación entre **{var_cuali}** y **{var_cuant}** (Categórica vs. Numérica)")
        fig5 = plt.figure(figsize=(10, 5))
        sns.boxplot(x=var_cuali, y=var_cuant, data=data)
        plt.xticks(rotation=45)
        st.pyplot(fig5)

    if len(cuali_vars) >= 2:
        st.markdown(f"### Tabla de Contingencia entre **{cuali_vars[0]}** y **{cuali_vars[1]}**")
        cont_table = pd.crosstab(data[cuali_vars[0]], data[cuali_vars[1]])
        st.dataframe(cont_table.reset_index())

        fig6, ax6 = plt.subplots(figsize=(10, 6))
        sns.heatmap(cont_table, annot=True, fmt="d", cmap="Blues", ax=ax6)
        ax6.set_title(f"Heatmap: {cuali_vars[0]} vs. {cuali_vars[1]}")
        st.pyplot(fig6)

# Análisis de Variables Cualitativas
with st.expander("Análisis de Variables Cualitativas (Frecuencias y Gráficos)", expanded=True):
    cuali_cols_disp = st.multiselect("Selecciona variables cualitativas:", cuali_vars, max_selections=3)

    for col in cuali_cols_disp:
        st.markdown(f"### Variable: `{col}`")

        frec_abs = data[col].value_counts()
        frec_rel = data[col].value_counts(normalize=True).round(3) * 100

        frec_df = pd.DataFrame({
            "Frecuencia Absoluta": frec_abs,
            "Frecuencia Relativa (%)": frec_rel
        })

        st.write("📊 Tabla de Frecuencias:")
        st.dataframe(frec_df)

        st.write("📊 Diagrama de Barras:")
        fig_bar, ax_bar = plt.subplots()
        frec_abs.plot(kind='bar', ax=ax_bar)
        ax_bar.set_title(f"Distribución de {col}")
        st.pyplot(fig_bar)

        st.write("🥧 Diagrama de Tortas:")
        fig_pie, ax_pie = plt.subplots()
        frec_abs.plot(kind='pie', autopct='%1.1f%%', ax=ax_pie)
        ax_pie.set_ylabel("")
        ax_pie.set_title(f"Distribución de {col}")
        st.pyplot(fig_pie)

        st.write(f"🔢 Número de categorías únicas: {data[col].nunique()}")

# 3. Análisis Univariado Optimizado
st.subheader("3. Análisis Univariado")

vars_interes = [
    "producto_precio_descuento",
    "producto_precio_con_oferta",
    "producto_precio_sin_oferta"
]

vars_validas = [var for var in vars_interes if var in data.columns]

if not vars_validas:
    st.warning("No se encontraron las variables de interés en el conjunto de datos.")
else:
    var_sel = st.selectbox("Selecciona una variable para analizar:", vars_validas)

    st.markdown(f"---\n### Análisis de: `{var_sel}`")
    st.write(data[var_sel].describe())
    st.write(f"**Media:** {data[var_sel].mean():,.2f}")
    st.write(f"**Mediana:** {data[var_sel].median():,.2f}")

    try:
        moda_serie = data[var_sel].mode()
        if not moda_serie.empty:
            st.write(f"**Moda:** {moda_serie[0]:,.2f}")
        else:
            st.write("**Moda:** No disponible")
    except Exception as e:
        st.write(f"**Moda:** Error al calcular: {e}")

    st.write(f"**Máximo:** {data[var_sel].max():,.2f}")
    st.write(f"**Mínimo:** {data[var_sel].min():,.2f}")

    fig1, ax1 = plt.subplots()
    sns.histplot(data[var_sel].dropna(), kde=True, ax=ax1)
    ax1.set_title(f"Histograma de {var_sel}")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    sns.boxplot(x=data[var_sel].dropna(), ax=ax2)
    ax2.set_title(f"Caja de Bigotes de {var_sel}")
    st.pyplot(fig2)

with st.expander("Conclusiones del Análisis Exploratorio", expanded=True):
    st.markdown("""
    - Se limpió y transformó exitosamente los precios de texto a valores numéricos.
    - Se identificaron variables clave para análisis univariado y bivariado.
    - Las visualizaciones ayudan a comprender la estructura y tendencias del dataset.
    """)

cursor.close()
connection.close()
