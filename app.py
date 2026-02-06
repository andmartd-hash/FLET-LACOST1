import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="IBM Pricing Tool", layout="wide")
st.title("💼 Cotizador IBM - Andresma")

# --- CARGA DE DATOS ROBUSTA ---
def buscar_y_cargar(keyword):
    archivos = os.listdir('.')
    for f in archivos:
        if keyword.lower() in f.lower() and f.endswith('.csv'):
            df = pd.read_csv(f)
            # Limpiamos espacios en blanco en los nombres de las columnas
            df.columns = df.columns.str.strip()
            return df
    return None

df_countries = buscar_y_cargar('countries')
df_lplat = buscar_y_cargar('lplat')
df_lband = buscar_y_cargar('lband')

if df_countries is not None and df_lplat is not None:
    # --- INTERFAZ ---
    st.sidebar.header("Parámetros")
    
    # Obtenemos lista de países y limpiamos cualquier espacio
    lista_paises = [p for p in df_countries.columns[2:]]
    pais_sel = st.sidebar.selectbox("Selecciona País", options=lista_paises)
    
    moneda = st.sidebar.radio("Moneda", ["USD", "Local"])
    
    # Exchange Rate
    try:
        er_val = float(df_countries.loc[1, pais_sel]) if moneda == "Local" else 1.0
    except:
        er_val = 1.0
    
    st.sidebar.metric("ER Aplicado", f"{er_val:,.2f}")

    # --- CÁLCULOS ---
    tipo_labor = st.radio("Tipo de Labor", ["Machine Category", "Brand Rate Full"], horizontal=True)
    df_actual = df_lplat if "Machine" in tipo_labor else df_lband
    
    # Limpiamos la columna de categorías para evitar el error de búsqueda
    opciones_labor = df_actual['MC/RR'].unique().tolist()
    seleccion = st.selectbox("Categoría", options=opciones_labor)
    
    # EL PUNTO DEL ERROR: Búsqueda segura
    row_labor = df_actual[df_actual['MC/RR'] == seleccion]
    
    if not row_labor.empty:
        try:
            # Usamos .iloc[0] para asegurar que tomamos el primer valor encontrado
            valor_mensual = float(row_labor[pais_sel].iloc[0])
            st.metric("Costo Mensual Detectado", f"${valor_mensual:,.2f}")
        except Exception as e:
            st.error(f"No se encontró el valor para {pais_sel} en la tabla de labor.")
            valor_mensual = 0.0
    else:
        valor_mensual = 0.0

    st.success(f"Sistema listo para procesar cotización en {pais_sel}")

else:
    st.error("Archivos CSV no encontrados en el repositorio de GitHub.")
