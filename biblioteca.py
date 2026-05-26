import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la interfaz
st.set_page_config(page_title="Mi Biblioteca Virtual", page_icon="📖", layout="centered")

st.title("Mi Biblioteca Virtual")
st.write("Bienvenido al catálogo digital. Aquí podés ver los libros disponibles y solicitar un préstamo.")

try:
    # 1. Reconstruimos el formato de credenciales de Google de forma dinámica y segura
    info_claves = {
        "type": "service_account",
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    
    # 2. Autenticación directa sin archivos locales
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    client = gspread.authorize(creds)
    
    # 3. Conexión a la planilla
    spreadsheet_id = "1fKr1898huosGb_-nZT_Jx25LhqsLA1gx0XQd5TLZeNI"
    sheet = client.open_by_key(spreadsheet_id)
    
    # Lectura de datos
    worksheet_libros = sheet.worksheet("Libros")
    data_libros = worksheet_libros.get_all_records()
    df = pd.DataFrame(data_libros)
    
    # Pestañas de navegación
    tab1, tab2 = st.tabs(["📖 Catálogo Disponibles", "🙋 Solicitar Préstamo"])

    with tab1:
        st.subheader("📚 Libros en Estantería")
        df['Disponibles'] = pd.to_numeric(df['Disponibles'], errors='coerce')
        libros_con_stock = df[df['Disponibles'] > 0]

        if not libros_con_stock.empty:
            st.dataframe(libros_con_stock[['Titulo', 'Autor']], width="stretch", hide_index=True)
        else:
            st.warning("Lo sentimos, no hay libros disponibles en este momento.")

    with tab2:
        st.subheader("🙋 Registrar Pedido de Préstamo")
        
        with st.form("formulario_prestamo", clear_on_submit=True):
            nombre_alumno = st.text_input("Nombre y Apellido del Alumno:")
            año_curso = st.selectbox("Año / Curso:", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
            
            lista_libros = libros_con_stock['Titulo'].tolist() if not libros_con_stock.empty else []
            libro_elegido = st.selectbox("Seleccioná el Libro:", lista_libros, index=None, placeholder="Escribí el nombre...")
            
            boton_enviar = st.form_submit_button("Confirmar Reserva de Libro")
            
            if boton_enviar:
                if nombre_alumno.strip() == "":
                    st.error("❌ Por favor, ingresá tu nombre antes de enviar.")
                elif libro_elegido is None:
                    st.error("❌ Por favor, seleccioná un libro de la lista.")
                else:
                    try:
                        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                        worksheet_prestamos = sheet.worksheet("Prestamos")
                        worksheet_prestamos.append_row([nombre_alumno, año_curso, libro_elegido, fecha_hoy])
                        
                        st.success(f"¡Listo, {nombre_alumno}! Tu solicitud para **'{libro_elegido}'** fue registrada.")
                        st.balloons()
                    except Exception as error_escritura:
                        st.error(f"Error al guardar en el Excel: {error_escritura}")

except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")