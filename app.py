import streamlit as st
import pandas as pd
import os

# Configuración de la interfaz
st.set_page_config(page_title="IBM Pricing Tool", layout="wide")
st.title("💼 Cotizador IBM - Andresma")

# --- CARGA DE DATOS SEGURA ---
@st.cache_data
def load_data():
    # Buscamos los archivos por palabras clave para evitar errores de nombres largos
    files = os.listdir('.')
    find = lambda x: next((f for f in files if x.lower() in f.lower() and f.endswith('.csv')), None)
    
    return {
        'countries': pd.read_csv(find('countries')) if find('countries') else None,
        'risk': pd.read_csv(find('risk')) if find('risk') else None,
        'offering': pd.read_csv(find('offering')) if find('offering') else None,
        'lplat': pd.read_csv(find('lplat')) if find('lplat') else None,
        'lband': pd.read_csv(find('lband')) if find('lband') else None
    }

data = load_data()

if data['countries'] is not None:
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.header("Parámetros Globales")
    lista_paises = data['countries'].columns[2:].tolist()
    pais = st.sidebar.selectbox("Selecciona País", options=lista_paises)
    moneda = st.sidebar.radio("Moneda de Cotización", ["USD", "Local"])
    
    # Lógica de Exchange Rate (ER): Fila 1 del archivo countries
    er = float(data['countries'].loc[1, pais]) if moneda == "Local" else 1.0
    st.sidebar.metric("Exchange Rate (ER)", f"{er:,.4f}")

    # --- CUERPO PRINCIPAL ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos del Servicio")
        customer = st.text_input("Nombre del Cliente", "IBM Customer")
        qty = st.number_input("Cantidad (QTY)", min_value=1, value=1)
        duration = st.number_input("Duración (Meses)", min_value=1, value=12)
        unit_cost = st.number_input("Costo Unitario USD", min_value=0.0, value=0.0)

    with col2:
        st.subheader("Labor / Management")
        tipo_labor = st.radio("Criterio de Labor", ["Machine Category", "Brand Rate Full"])
        df_labor = data['lplat'] if tipo_labor == "Machine Category" else data['lband']
        
        opcion_labor = st.selectbox("Categoría Seleccionada", options=df_labor['MC/RR'].unique())
        
    # --- CÁLCULOS FINALES ---
    # 1. Costo de Servicio
    total_service = (unit_cost * duration * qty)
    
    # 2. Costo de Labor (buscado en tabla por país)
    row_labor = df_labor[df_labor['MC/RR'] == opcion_labor]
    monthly_labor = float(row_labor[pais].values[0]) if not row_labor.empty else 0
    total_manage = monthly_labor * duration

    st.divider()
    
    # --- DASHBOARD DE RESULTADOS ---
    r1, r2, r3 = st.columns(3)
    r1.metric("Total Service", f"${total_service:,.2f}")
    r2.metric("Total Manage (Labor)", f"${total_manage:,.2f}")
    r3.metric("TOTAL COTIZACIÓN", f"${(total_service + total_manage):,.2f}", delta_color="inverse")

    if st.button("🚀 Procesar y Guardar"):
        st.balloons()
        st.success(f"Cotización para {customer} lista.")
else:
    st.error("No se encontraron los archivos CSV. Asegúrate de que estén en la misma carpeta.")