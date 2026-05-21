import streamlit as st
import pandas as pd
import psycopg2
import os
from pathlib import Path

# Configuración
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
st.set_page_config(page_title="Control Pro", layout="centered")

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

st.title("💰 Control de Gastos y Archivos")

tab1, tab2 = st.tabs(["📊 Gastos", "📂 Archivos"])

with tab1:
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

    conn = get_db()
    df = pd.read_sql("SELECT * FROM productos", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.metric("Total registrado", f"S/ {df['precio'].sum():,.2f}")
        if st.button("Limpiar registros"):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM productos")
            conn.commit()
            conn.close()
            st.rerun()
    else:
        st.info("No hay gastos registrados.")

with tab2:
    uploaded_file = st.file_uploader("Subir documento")
    if uploaded_file:
        with open(UPLOAD_DIR / uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Archivo {uploaded_file.name} guardado.")
    
    st.subheader("Archivos en servidor")
    st.write(os.listdir(UPLOAD_DIR))
