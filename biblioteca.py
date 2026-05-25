import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la pestaña del navegador
st.set_page_config(page_title="Biblioteca Virtual", page_icon="📚", layout="centered")

# --- BARRA LATERAL (ESCUDO) ---
with st.sidebar:
    # Copiá acá el link de la imagen del escudo de tu colegio. Si no tenés, dejá esta de prueba.
    st.image("https://cdn-icons-png.flaticon.com/512/2228/2228722.png", width=120)
    st.title("Navegación")
    st.markdown("Sistema de Gestión de Libros")
    st.info("Desarrollado para la bitácora de proyecto institucional.")

# --- TÍTULO PRINCIPAL ---
st.title("📚 Mi Biblioteca Virtual")
st.markdown("Bienvenido al catálogo digital. Aquí podés ver los libros disponibles y solicitar un préstamo.")
st.divider()

# --- CONEXIÓN A BASE DE DATOS (GOOGLE SHEETS) ---
# Poné tu link real acá abajo
url = "https://docs.google.com/spreadsheets/d/1YeDJ2Mp7YRj1wW5ktGAly3kbPANAOvQXTT9_r1eE608/edit?usp=sharing"

try:
    # ttl=0 hace que refresque la info al instante si cambia el Excel
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0)

    # --- TABLA DE STOCK INTELIGENTE ---
    st.subheader("📖 Libros en Estantería")
    
    # Filtramos: Solo mostramos los libros cuyo estado sea 1 (Disponible)
    # Convertimos a número por las dudas
    df['Estado'] = pd.to_numeric(df['Estado'], errors='coerce')
    disponibles = df[df['Estado'] == 1]

    if not disponibles.empty:
        # Mostramos una tabla limpia solo con Título y Autor
        st.dataframe(disponibles[['titulo', 'autor']], width="stretch", hide_index=True)
    else:
        st.warning("Lo sentimos, no hay libros disponibles en este momento.")

    # --- FORMULARIO DE PRÉSTAMO ---
    st.divider()
    st.subheader("🙋‍♂️ Solicitar Préstamo")

    with st.form("form_prestamo", clear_on_submit=True):
        nombre = st.text_input("Nombre y Apellido del Alumno:")
        grado = st.selectbox("Año / Curso:", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
        
        # El menú dinámico: solo da a elegir los libros filtrados arriba
        lista_titulos = disponibles['titulo'].tolist() if not disponibles.empty else ["No hay stock"]
        libro = st.selectbox("Seleccioná el libro que querés llevarte:", lista_titulos)
        
        enviar = st.form_submit_button("Confirmar Solicitud")

        if enviar:
            if nombre.strip() == "":
                st.error("❌ Por favor, ingresá tu nombre antes de enviar.")
            elif libro == "No hay stock":
                st.error("❌ No podés solicitar préstamos si no hay stock disponible.")
            else:
                st.success(f"¡Listo, {nombre}! Tu solicitud para **'{libro}'** fue registrada. Pasá por biblioteca a retirarlo.")

except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")

# --- FOOTER PROFESIONAL ---
st.divider()
st.markdown(
    """
    <style>
    .footer { text-align: center; color: #888888; font-size: 13px; margin-top: 50px; }
    </style>
    <div class="footer">
        © 2026 Proyecto Biblioteca Escolar • Diseñado para Think Digital Hub
    </div>
    """, 
    unsafe_allow_html=True
)