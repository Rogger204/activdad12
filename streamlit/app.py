import streamlit as st
import pandas as pd
import psycopg2
import os

# Configuración básica
st.set_page_config(page_title="Mi Presupuesto", layout="centered")

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

st.title("💰 Control de Gastos")

# Formulario simple
with st.expander("➕ Añadir nuevo gasto"):
    with st.form("gasto_form", clear_on_submit=True):
        nombre = st.text_input("Concepto")
        monto = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Registrar"):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO productos (nombre, precio) VALUES (%s, %s)", (nombre, monto))
            conn.commit()
            conn.close()
            st.rerun()

# Carga de datos
conn = get_db()
df = pd.read_sql("SELECT * FROM productos", conn)
conn.close()

# Visualización más limpia
st.subheader("Resumen de tus gastos")

if not df.empty:
    # Filtro visual simple
    limite = st.slider("Filtrar gastos mayores a:", 0, int(df['precio'].max()), 0)
    df_filtrado = df[df['precio'] >= limite]
    
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Métricas rápidas
    total = df['precio'].sum()
    st.metric("Total gastado", f"S/ {total:,.2f}")
else:
    st.info("No hay gastos registrados aún.")

# Botón para borrar todo (más práctico que borrar uno por uno)
if st.button("Limpiar registros"):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos")
    conn.commit()
    conn.close()
    st.rerun()
