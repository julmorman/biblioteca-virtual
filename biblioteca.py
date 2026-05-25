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

# Importamos datetime para registrar el día del préstamo automáticamente
    from datetime import datetime

    # --- PESTAÑAS DE LA APLICACIÓN ---
    tab1, tab2 = st.tabs(["Catálogo Disponibles", "Solicitar Préstamo"])

    with tab1:
        st.subheader("Libros en Estantería")
        
        # Convertimos la columna 'Disponibles' a números por seguridad
        df['Disponibles'] = pd.to_numeric(df['Disponibles'], errors='coerce')
        
        # Filtramos para mostrar solo los que tienen stock real en el colegio
        libros_con_stock = df[df['Disponibles'] > 0]

        if not libros_con_stock.empty:
            st.dataframe(libros_con_stock[['Titulo', 'Autor']], width="stretch", hide_index=True)
        else:
            st.warning("Lo sentimos, no hay libros disponibles en este momento.")

    with tab2:
        st.subheader("Registrar Pedido de Préstamo")
        
        with st.form("formulario_prestamo", clear_on_submit=True):
            nombre_alumno = st.text_input("Nombre y Apellido del Alumno:")
            año_curso = st.selectbox("Año / Curso:", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
            
            if not libros_con_stock.empty:
                lista_libros = libros_con_stock['Titulo'].tolist()
            else:
                lista_libros = []
                
            # CORRECCIÓN DE UI: index=None hace que arranque vacío sin preseleccionar nada
            libro_elegido = st.selectbox(
                "Seleccioná el Libro que querés llevarte:", 
                lista_libros, 
                index=None, 
                placeholder="Empezá a escribir el nombre del libro..."
            )
            
            boton_enviar = st.form_submit_button("Confirmar Reserva de Libro")
            
            if boton_enviar:
                if nombre_alumno.strip() == "":
                    st.error("Por favor, ingresá tu nombre antes de enviar.")
                elif libro_elegido is None:
                    st.error("Por favor, seleccioná un libro de la lista.")
                else:
                    try:
                        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                        
                        # 1. Intentamos leer lo que ya hay en la pestaña de préstamos para acumular datos
                        try:
                            df_prestamos_existente = conn.read(spreadsheet=url, worksheet="Prestamos", ttl=0)
                        except:
                            df_prestamos_existente = pd.DataFrame(columns=["Alumno", "Curso", "Libro", "Fecha"])
                        
                        # 2. Armamos la nueva fila como un DataFrame ordenado
                        nueva_fila = pd.DataFrame([[nombre_alumno, año_curso, libro_elegido, fecha_hoy]], 
                                                  columns=["Alumno", "Curso", "Libro", "Fecha"])
                        
                        # 3. Juntamos el historial existente con la nueva reserva
                        if not df_prestamos_existente.empty:
                            df_actualizado = pd.concat([df_prestamos_existente, nueva_fila], ignore_index=True)
                        else:
                            df_actualizado = nueva_fila
                        
                        # 4. CORRECCIÓN DE ESCRITURA: Usamos .update() que reescribe la tabla con el dato nuevo sumado
                        conn.update(
                            worksheet="Prestamos",
                            data=df_actualizado,
                        )
                        
                        st.success(f"¡Listo, {nombre_alumno}! Tu solicitud para **'{libro_elegido}'** fue registrada. Pasá por biblioteca.")
                        st.balloons() # ¡Que vuelen los globos!
                        
                    except Exception as error_escritura:
                        st.error(f"Error al guardar en el Excel: {error_escritura}")
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