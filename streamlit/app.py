import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os
from pathlib import Path

# Configuración
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
st.set_page_config(page_title="Control NoSQL", layout="centered")

# Conexión a MongoDB
def get_db():
    client = MongoClient("mongodb://mongo:27017/")
    return client["demo_db"]

st.title("💰 Control de Gastos (MongoDB)")

tab1, tab2 = st.tabs(["📊 Gastos", "📂 Archivos"])

with tab1:
    with st.expander("➕ Añadir nuevo gasto"):
        with st.form("gasto_form", clear_on_submit=True):
            nombre = st.text_input("Concepto")
            monto = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("Registrar"):
                db = get_db()
                db.productos.insert_one({"nombre": nombre, "precio": monto})
                st.rerun()

    db = get_db()
    data = list(db.productos.find({}, {"_id": 0})) # Traer todo excepto el ID de Mongo
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.metric("Total registrado", f"S/ {df['precio'].sum():,.2f}")
        
        if st.button("Limpiar registros"):
            db.productos.delete_many({})
            st.rerun()
    else:
        st.info("No hay gastos registrados.")

with tab2:
    uploaded_file = st.file_uploader("Subir documento")
    if uploaded_file:
        with open(UPLOAD_DIR / uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Guardado.")
    
    st.write("Archivos:", os.listdir(UPLOAD_DIR))
