import streamlit as st
import pandas as pd
import requests
import io
# Ya no necesitamos BeautifulSoup porque vamos directo al Excel

# Configuración de la página
st.set_page_config(page_title="Cómo amaneció el mercado", layout="wide")

st.title("🇩🇴 ¿Cómo amaneció el mercado?")
st.write("Precios actualizados directamente desde el Ministerio de Agricultura.")

# --- INICIO DE LA FUNCIÓN DE DESCARGA Y LECTURA ---
# Se actualiza cada hora para no saturar el servidor del gobierno
@st.cache_data(ttl=3600) 
def obtener_datos():
    
    # 🚨🚨🚨 PUNTO CRÍTICO QUE DEBES CAMBIAR DIARIAMENTE 🚨🚨🚨
    # El archivo Excel tiene la fecha en el nombre. Esta URL debe ser actualizada
    # cada vez que el Ministerio publique un nuevo informe (ej: 04-12-2025).
    # Si esta URL no existe, el robot fallará.
    url_base = "https://agricultura.gob.do/wp-content/uploads/2025/12/Informe-de-Precios-03-12-2025.xlsx"
    
    try:
        # 1. Descargar el Excel directamente desde la URL
        excel_data = requests.get(url_base).content
        
        # 2. Leer el Excel, ignorando las primeras 5 filas (para saltar logos y títulos)
        # La tabla empieza en la Fila 6, por eso usamos header=5
        df = pd.read_excel(io.BytesIO(excel_data), header=5)
        
        return df, url_base
        
    except Exception as e:
        # Si falla, es por la URL incorrecta o el archivo no existe.
        st.error(f"❌ ¡ERROR! No se pudo leer el reporte de hoy. Por favor, asegúrate de que la fecha en el enlace sea la más reciente.")
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
