import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de la interfaz
st.set_page_config(page_title="Mi Biblioteca Virtual", page_icon="📖", layout="centered")

st.title("Mi Biblioteca Virtual")
st.write("Bienvenido al catálogo digital. Aquí podés ver los libros disponibles y solicitar un préstamo.")

try:
    # 1. Conexión nativa (usa el secreto 'connections.gsheets.spreadsheet')
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Lectura directa
    df = conn.read(worksheet="Libros")
    
    # 3. Pestañas
    tab1, tab2 = st.tabs(["📖 Catálogo Disponibles", "🙋 Solicitar Préstamo"])

    with tab1:
        st.subheader("📚 Libros en Estantería")
        df['Disponibles'] = pd.to_numeric(df['Disponibles'], errors='coerce')
        libros_con_stock = df[df['Disponibles'] > 0]

        if not libros_con_stock.empty:
            st.dataframe(libros_con_stock[['Titulo', 'Autor']], hide_index=True)
        else:
            st.warning("Lo sentimos, no hay libros disponibles en este momento.")

    with tab2:
        st.subheader("🙋 Registrar Pedido de Préstamo")
        with st.form("formulario_prestamo", clear_on_submit=True):
            nombre = st.text_input("Nombre y Apellido del Alumno:")
            curso = st.selectbox("Año / Curso:", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
            lista_libros = libros_con_stock['Titulo'].tolist() if not libros_con_stock.empty else []
            libro = st.selectbox("Seleccioná el Libro:", lista_libros, index=None, placeholder="Escribí el nombre...")
            
            if st.form_submit_button("Confirmar Reserva de Libro"):
                if nombre.strip() == "" or libro is None:
                    st.error("❌ Por favor, completá todos los campos.")
                else:
                    # Escribimos directo en la hoja 'Prestamos'
                    nuevo_registro = pd.DataFrame([[nombre, curso, libro, datetime.now().strftime("%d/%m/%Y")]])
                    conn.create(worksheet="Prestamos", data=nuevo_registro)
                    st.success(f"¡Listo, {nombre}! Tu solicitud para '{libro}' fue registrada.")
                    st.balloons()

except Exception as e:
    st.error(f"Error de conexión: {e}")