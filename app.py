import streamlit as st
import pandas as pd
import requests
import io
import datetime 

# Configuración de la página
st.set_page_config(page_title="Cómo amaneció el mercado", layout="wide")

st.title("🇩🇴 ¿Cómo amaneció el mercado?")
st.write("Precios actualizados directamente desde el Ministerio de Agricultura.")

# --- INICIO DE LA FUNCIÓN DE DESCARGA Y LECTURA ---
# Se actualiza cada hora para no saturar el servidor del gobierno
@st.cache_data(ttl=3600) 
def obtener_datos():
    
    # 1. Definimos el disfraz de navegador (User-Agent) para evitar el bloqueo del servidor
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    hoy = datetime.date.today()
    ayer = hoy - datetime.timedelta(days=1)
    
    # 2. Intentar Hoy: Generamos la URL del informe con la fecha actual
    fecha_hoy = hoy.strftime("%d-%m-%Y")
    url_hoy = f"https://agricultura.gob.do/wp-content/uploads/{hoy.strftime('%Y')}/{hoy.strftime('%m')}/Informe-de-Precios-{fecha_hoy}.xlsx"
    
    try:
        st.info(f"⏳ Buscando reporte del día: {fecha_hoy}...")
        # Usamos el disfraz (headers=headers)
        excel_data = requests.get(url_hoy, headers=headers).content
        df = pd.read_excel(io.BytesIO(excel_data), header=5)
        st.success(f"✅ Reporte del {fecha_hoy} cargado correctamente.")
        return df, url_hoy
    
    except:
        # 3. Si Hoy falla, intentamos AYER (Fallback)
        st.warning(f"⚠️ El reporte del {fecha_hoy} no ha sido publicado. Intentando cargar reporte de AYER...")
        fecha_ayer = ayer.strftime("%d-%m-%Y")
        url_ayer = f"https://agricultura.gob.do/wp-content/uploads/{ayer.strftime('%Y')}/{ayer.strftime('%m')}/Informe-de-Precios-{fecha_ayer}.xlsx"
        
        try:
            # Usamos el disfraz (headers=headers)
            excel_data = requests.get(url_ayer, headers=headers).content
            df = pd.read_excel(io.BytesIO(excel_data), header=5)
            st.success(f"✅ Reporte del {fecha_ayer} (ayer) cargado correctamente.")
            return df, url_ayer
        
        except Exception as e:
            # Si ambos fallan, mostramos el error
            st.error(f"❌ ¡ERROR CRÍTICO! No se pudo leer ni el reporte de hoy ni el de ayer. El servidor del gobierno puede estar bloqueando la solicitud o los archivos no están disponibles.")
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
