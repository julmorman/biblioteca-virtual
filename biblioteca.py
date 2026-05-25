import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Biblioteca Virtual", page_icon="📖", layout="centered")

st.title("Mi Biblioteca Virtual")
st.write("Bienvenido al catálogo digital. Aquí podés ver los libros disponibles y solicitar un préstamo.")

try:
    # 1. CREAMOS LA CONEXIÓN USANDO LOS SECRETS AUTOMÁTICAMENTE
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. LEEMOS EL CATÁLOGO DE LIBROS (Ponemos ttl=0 para que se actualice al instante)
    df = conn.read(worksheet="Libros", ttl=0)

    # --- PESTAÑAS DE LA APLICACIÓN ---
    tab1, tab2 = st.tabs(["📖 Catálogo Disponibles", "🙋 Solicitar Préstamo"])

    with tab1:
        st.subheader("📚 Libros en Estantería")
        
        # Limpiamos y convertimos la columna 'Disponibles' a números
        df['Disponibles'] = pd.to_numeric(df['Disponibles'], errors='coerce')
        
        # Filtramos para mostrar solo los que tienen stock real
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
            
            if not libros_con_stock.empty:
                lista_libros = libros_con_stock['Titulo'].tolist()
            else:
                lista_libros = []
                
            # Buscador predictivo que arranca limpio
            libro_elegido = st.selectbox(
                "Seleccioná el Libro que querés llevarte:", 
                lista_libros, 
                index=None, 
                placeholder="Empezá a escribir el nombre del libro..."
            )
            
            boton_enviar = st.form_submit_button("Confirmar Reserva de Libro")
            
            if boton_enviar:
                if nombre_alumno.strip() == "":
                    st.error("❌ Por favor, ingresá tu nombre antes de enviar.")
                elif libro_elegido is None:
                    st.error("❌ Por favor, seleccioná un libro de la lista.")
                else:
                    try:
                        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                        
                        # Intentamos leer el historial existente en Prestamos
                        try:
                            df_prestamos_existente = conn.read(worksheet="Prestamos", ttl=0)
                        except:
                            df_prestamos_existente = pd.DataFrame(columns=["Alumno", "Curso", "Libro", "Fecha"])
                        
                        # Armamos la nueva fila
                        nueva_fila = pd.DataFrame([[nombre_alumno, año_curso, libro_elegido, fecha_hoy]], 
                                                  columns=["Alumno", "Curso", "Libro", "Fecha"])
                        
                        # Consolidamos las tablas
                        if not df_prestamos_existente.empty:
                            df_actualizado = pd.concat([df_prestamos_existente, nueva_fila], ignore_index=True)
                        else:
                            df_actualizado = nueva_fila
                        
                        # Guardamos de forma segura con .update() usando la cuenta de servicio
                        conn.update(
                            worksheet="Prestamos",
                            data=df_actualizado,
                        )
                        
                        st.success(f"¡Listo, {nombre_alumno}! Tu solicitud para **'{libro_elegido}'** fue registrada. Pasá por biblioteca.")
                        st.balloons()
                        
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