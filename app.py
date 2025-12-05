import streamlit as st
import pandas as pd
import requests
import io
import datetime 
# Importamos 'datetime' para calcular la fecha de hoy automáticamente.

# Configuración de la página
st.set_page_config(page_title="Cómo amaneció el mercado", layout="wide")

st.title("🇩🇴 ¿Cómo amaneció el mercado?")
st.write("Precios actualizados directamente desde el Ministerio de Agricultura.")

# --- INICIO DE LA FUNCIÓN DE DESCARGA Y LECTURA ---
# Se actualiza cada hora para no saturar el servidor del gobierno
@st.cache_data(ttl=3600) 
def obtener_datos():
    
    # ** CÓDIGO CLAVE PARA AUTOMATIZAR LA FECHA **
    hoy = datetime.date.today()
    # Formato de fecha del archivo: DD-MM-YYYY (ej: 04-12-2025)
    fecha_str = hoy.strftime("%d-%m-%Y")
    # Formato de año y mes para la ruta de la URL (ej: /2025/12/)
    anio_str = hoy.strftime("%Y")
    mes_str = hoy.strftime("%m")
    
    # Construimos la URL usando la fecha actual. 
    # Ejemplo de URL: https://agricultura.gob.do/wp-content/uploads/2025/12/Informe-de-Precios-04-12-2025.xlsx
    url_base = f"https://agricultura.gob.do/wp-content/uploads/{anio_str}/{mes_str}/Informe-de-Precios-{fecha_str}.xlsx"
    
    try:
        # 1. Descargar el Excel directamente desde la URL
        excel_data = requests.get(url_base).content
        
        # 2. Leer el Excel, ignorando las primeras 5 filas (para saltar logos y títulos)
        # La tabla de precios empieza en la Fila 6, por eso usamos header=5
        df = pd.read_excel(io.BytesIO(excel_data), header=5)
        
        return df, url_base
        
    except Exception as e:
        # Si falla, es porque el archivo del día no ha sido publicado o no existe.
        st.error(f"❌ ¡ERROR! No se pudo leer el reporte de hoy ({fecha_str}). El archivo aún no está disponible o la URL ha cambiado. Por favor, intenta más tarde.")
        return None, None
# --- FIN DE LA FUNCIÓN DE DESCARGA Y LECTURA ---

# --- EJECUCIÓN Y VISUALIZACIÓN ---
df, url_fuente = obtener_datos()

if df is not None:
    # Limpieza básica
    df = df.dropna(how='all')
    
    # Buscador y Tabla
    st.subheader("Búsqueda y Tabla de Precios")
    producto = st.text_input("🔍 Busca un producto (ej: Yuca, Arroz, Pollo)", "")
    
    if producto:
        # Filtrar por el término
        df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(producto, case=False).any(), axis=1)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        # Mostrar todo
        st.dataframe(df, use_container_width=True)
        
    st.caption(f"Fuente oficial del reporte: [Descargar Excel Original]({url_fuente})")
else:
    # El error se muestra en la función, no necesitamos hacer nada aquí.
    pass 

# Quita la marca de agua de Streamlit para una apariencia más limpia
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
