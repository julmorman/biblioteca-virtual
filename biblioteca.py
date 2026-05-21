import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Título de tu web
st.title("Biblioteca Virtual")

# 1. Conexión con Google Sheets
# Reemplaza el link de abajo por el de tu planilla (asegurate que sea pública)
url = "https://docs.google.com/spreadsheets/d/1YeDJ2Mp7YRj1wW5ktGAly3kbPANAOvQXTT9_r1eE608/edit?usp=sharing/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)

    # 2. Mostrar los datos
    st.write("### Libros disponibles actualmente:")
    st.dataframe(df)

except Exception as e:
    st.error(f"Ocurrió un error al conectar: {e}")