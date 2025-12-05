import streamlit as st
import pandas as pd
import io
# Ya no necesitamos 'requests' ni 'datetime' porque no hacemos scraping

# Configuración de la página
st.set_page_config(page_title="Cómo amaneció el mercado", layout="wide")

st.title("🇩🇴 ¿Cómo amaneció el mercado?")
st.write("Precios actualizados por el administrador (Tú) con información del Ministerio de Agricultura.")

# --- INICIO DE LA FUNCIÓN DE LECTURA DE GOOGLE SHEETS ---
@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def obtener_datos():
    
    # 🚨🚨🚨 INSTRUCCIÓN IMPORTANTE 🚨🚨🚨
    # Reemplaza 'EL_ID_DE_TU_HOJA' con el ID que encuentras en la URL de tu Google Sheet.
    GOOGLE_SHEET_ID = 'EL_ID_DE_TU_HOJA'
    
    # URL de exportación a CSV de la hoja 'Detallista'
    url_base = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Detallista'
    
    try:
        st.info("⏳ Leyendo el reporte de precios de la hoja de cálculo...")
        
        # Pandas lee el CSV de Google Sheets directamente
        # skiprows=5 porque el archivo original tiene 5 filas de encabezado antes de la data
        df = pd.read_csv(url_base, skiprows=5)
        
        # Tomamos la fecha de la tercera fila del archivo original, que ahora es la fila 3
        # Esto asume que copias y pegas incluyendo las filas de encabezado del archivo original
        fecha_reporte = pd.read_csv(url_base, header=None, skiprows=2, nrows=1).iloc[0, 0]
        
        st.success(f"✅ Reporte del {fecha_reporte} cargado correctamente desde tu Google Sheet.")
        return df, url_base
        
    except Exception as e:
        st.error(f"❌ ¡ERROR CRÍTICO! No se pudo leer el archivo de Google Sheets. Asegúrate de que el ID sea correcto y que la hoja 'Detallista' sea pública.")
        return None, None
# --- FIN DE LA FUNCIÓN DE LECTURA ---

# --- EJECUCIÓN Y VISUALIZACIÓN ---
df, url_fuente = obtener_datos()

if df is not None:
    # Limpieza: Eliminamos filas completamente vacías y la columna extra (Unnamed)
    df = df.dropna(how='all', axis=0)
    df = df.dropna(axis=1, how='all')
    if 'Unnamed: 7' in df.columns:
        df = df.drop(columns=['Unnamed: 7'])
    
    # Ajustar el nombre de las columnas (basado en tu archivo CSV)
    df.columns = ['PRODUCTOS', 'UNID', 'MERCADOS_NUEVO', 'MERCADOS_CONAPROPE', 'MERCADOS_LOS MINA', 'MERCADOS_V. CONSUELO', 'MERCADOS_CRISTO REY', 'MERCADOM', 'SUPERMERCADO']
    
    # Buscador y Tabla
    st.subheader("Búsqueda y Tabla de Precios Detallistas")
    producto = st.text_input("🔍 Busca un producto (ej: Yuca, Arroz, Pollo)", "")
    
    if producto:
        df_filtrado = df[df['PRODUCTOS'].astype(str).str.contains(producto, case=False, na=False)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
        
    st.caption(f"Fuente de datos: Tu Hoja de Cálculo Privada (Actualización manual)")
else:
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
