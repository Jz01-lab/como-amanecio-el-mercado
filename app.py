import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Configuración de la página
st.set_page_config(page_title="Cómo amaneció el mercado", layout="wide")

st.title("🇩🇴 ¿Cómo amaneció el mercado?")
st.write("Precios actualizados directamente desde el Ministerio de Agricultura.")

# Función para obtener los datos (El Robot)
@st.cache_data(ttl=3600) # Se actualiza cada hora para no saturar
def obtener_datos():
    url_base = "https://agricultura.gob.do/category/estadisticas-agropecuarias/precios-de-productos-agropecuarios/2-datos-inter-diarios-de-precios-de-mercados-y-supermercados-de-sto-dgo/precios-inter-diarios-del-mes-de-junio/"
    
    try:
        # 1. Ir a la web
        response = requests.get(url_base)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 2. Búsqueda final: Intentar encontrar el botón de descarga por su etiqueta 'save_alt'
        # Esto asume que el icono de descarga se identifica en el HTML
        link = soup.find('a', attrs={'title': 'Descargar'})
        
        # Si no lo encuentra por título, buscar el primer enlace que lleve a un archivo Excel
        if not link:
            link = soup.find('a', href=lambda href: href and ('.xlsx' in href or '.xls' in href))
        
        if link:
            url_excel = link['href']
            # 3. Descargar el Excel en memoria
            excel_data = requests.get(url_excel).content
            
            # 4. Leer el Excel (ajustamos header=5 para ignorar logos, títulos y notas iniciales)
            df = pd.read_excel(io.BytesIO(excel_data), header=5)
            return df, url_excel
        else:
            return None, None
    except Exception as e:
        st.error(f"Error conectando con Agricultura: {e}")
        return None, None

# Ejecutar el robot
df, url_fuente = obtener_datos()

if df is not None:
    # Limpieza básica (Eliminar filas vacías si las hay)
    df = df.dropna(how='all')
    
    # Buscador de productos
    producto = st.text_input("🔍 Busca un producto (ej: Yuca, Arroz, Pollo)", "")
    
    if producto:
        # Filtrar si el usuario escribió algo
        df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(producto, case=False).any(), axis=1)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        # Mostrar todo
        st.dataframe(df, use_container_width=True)
        
    st.caption(f"Fuente oficial: [Descargar Excel Original]({url_fuente})")
else:
    st.warning("No pudimos leer el reporte de hoy. Intenta más tarde.")

# Nota para ti: Esto quita la marca de agua de Streamlit para que se vea más pro
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
