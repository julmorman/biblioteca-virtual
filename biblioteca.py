import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Mi Biblioteca Virtual", page_icon="📖", layout="centered")

st.title("Mi Biblioteca Virtual")
st.write("Bienvenido al catálogo digital. Aquí podés ver los libros disponibles y solicitar un préstamo.")

try:
    # Levanta la clave con comillas triples y limpia saltos dobles si el navegador los metió
    raw_key = st.secrets["connections"]["gsheets"]["private_key"]
    
    # Conectamos usando el gestor interno de Streamlit
    conn = st.connection("gsheets", type=GSheetsConnection)
    url_excel = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # Leemos la hoja de libros
    df = conn.read(spreadsheet=url_excel, worksheet="Libros", ttl=0)
    
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
                        
                        try:
                            df_prestamos_existente = conn.read(spreadsheet=url_excel, worksheet="Prestamos", ttl=0)
                            if df_prestamos_existente is None or df_prestamos_existente.empty:
                                df_prestamos_existente = pd.DataFrame(columns=["Alumno", "Curso", "Libro", "Fecha"])
                        except:
                            df_prestamos_existente = pd.DataFrame(columns=["Alumno", "Curso", "Libro", "Fecha"])
                        
                        nueva_fila = pd.DataFrame([[nombre_alumno, año_curso, libro_elegido, fecha_hoy]], columns=["Alumno", "Curso", "Libro", "Fecha"])
                        df_prestamos_existente.columns = ["Alumno", "Curso", "Libro", "Fecha"]
                        df_actualizado = pd.concat([df_prestamos_existente, nueva_fila], ignore_index=True)
                        
                        conn.update(spreadsheet=url_excel, worksheet="Prestamos", data=df_actualizado)
                        st.success(f"¡Listo, {nombre_alumno}! Tu solicitud para **'{libro_elegido}'** fue registrada.")
                        st.balloons()
                    except Exception as error_escritura:
                        st.error(f"Error al guardar en el Excel: {error_escritura}")

except Exception as e:
    st.error(f"Error de credenciales o configuración: {e}")

st.divider()
st.markdown('<div style="text-align: center; color: #888888; font-size: 13px;">© 2026 Proyecto Biblioteca Escolar</div>', unsafe_allow_html=True)