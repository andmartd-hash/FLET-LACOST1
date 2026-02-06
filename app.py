import streamlit as st
import pandas as pd
import os

# Configuración de página estilo Dashboard Financiero
st.set_page_config(page_title="IBM Quote Engine", layout="wide", initial_sidebar_state="expanded")

# Estilo CSS para mejorar la apariencia (Bordes, sombras y fuentes)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_all_data():
    files = os.listdir('.')
    def find(k): return next((f for f in files if k.lower() in f.lower() and f.endswith('.csv')), None)
    
    data = {
        'ui': pd.read_csv(find('UI_CONGIF')) if find('UI_CONGIF') else None,
        'countries': pd.read_csv(find('countries')) if find('countries') else None,
        'risk': pd.read_csv(find('risk')) if find('risk') else None,
        'offering': pd.read_csv(find('offering')) if find('offering') else None,
        'lplat': pd.read_csv(find('lplat')) if find('lplat') else None,
        'lband': pd.read_csv(find('lband')) if find('lband') else None,
        'slc': pd.read_csv(find('slc')) if find('slc') else None
    }
    # Limpieza de nombres de columnas
    for df in data.values():
        if df is not None: df.columns = df.columns.str.strip()
    return data

data = load_all_data()

if data['ui'] is not None:
    st.title("📊 IBM Pricing & Service Tool")
    
    # --- BARRA LATERAL (Siguiendo UI_CONFIG) ---
    with st.sidebar:
        st.header("Configuración Base")
        # El ID_Cotizacion y otros campos vienen de la fila 3 (test value) o manual
        id_cot = st.text_input("ID Cotización", value="COT-001")
        
        lista_paises = data['countries'].columns[2:].tolist() if data['countries'] is not None else []
        pais_sel = st.selectbox("País", options=lista_paises)
        
        moneda = st.selectbox("Currency", ["USD", "Local"])
        
        # Lógica de Exchange Rate del archivo countries
        er_val = 1.0
        if moneda == "Local" and data['countries'] is not None:
            er_val = float(data['countries'].loc[1, pais_sel])
        st.metric("Exchange Rate", f"{er_val:,.2f}")
        
        riesgo = st.selectbox("QA Risk", options=data['risk']['Risk'].tolist() if data['risk'] is not None else ["Low"])

    # --- CUERPO PRINCIPAL (Módulos de UI_CONFIG) ---
    tabs = st.tabs(["Servicios e Infraestructura", "Módulo Management (Labor)", "Análisis Financiero"])

    with tabs[0]:
        st.subheader("Modulo Servicios")
        c1, c2, c3 = st.columns(3)
        with c1:
            customer = st.text_input("Customer Name", placeholder="Ingrese cliente")
            offering = st.selectbox("Offering", options=data['offering']['Offering'].tolist() if data['offering'] is not None else [])
        with c2:
            qty = st.number_input("QTY", min_value=1, value=1)
            slc = st.selectbox("SLC", options=data['slc']['SLC'].tolist() if data['slc'] is not None else [])
        with c3:
            unit_cost = st.number_input("Unit Cost USD", min_value=0.0, format="%.2f")
            duration = st.number_input("Duration (Months)", min_value=1, value=12)

    with tabs[1]:
        st.subheader("Modulo Managment")
        m1, m2 = st.columns(2)
        with m1:
            mcbr = st.radio("MachCat / BandRate", ["Machine Category", "Brand Rate Full"], horizontal=True)
        with m2:
            df_labor = data['lplat'] if "Machine" in mcbr else data['lband']
            cat_labor = st.selectbox("MC / RR", options=df_labor['MC/RR'].unique().tolist() if df_labor is not None else [])

    # --- CÁLCULOS Y RESULTADOS ---
    # Cálculo Labor (Búsqueda segura con iloc)
    row_labor = df_labor[df_labor['MC/RR'] == cat_labor]
    costo_mensual = 0.0
    if not row_labor.empty:
        costo_mensual = float(row_labor[pais_sel].iloc[0])

    total_service = (unit_cost * duration * qty)
    total_manage = (costo_mensual * duration)
    total_final = total_service + total_manage

    st.divider()
    
    # Mostrar resultados finales con estética mejorada
    res1, res2, res3 = st.columns(3)
    res1.metric("Total Service Cost", f"${total_service:,.2f}")
    res2.metric("Total Manage Cost", f"${total_manage:,.2f}")
    res3.metric("TOTAL CONSOLIDADO", f"${total_final:,.2f}", delta="Cálculo Final", delta_color="normal")

    if st.button("💾 Guardar y Sincronizar con GitHub"):
        st.balloons()
        st.info(f"Cotización {id_cot} para {customer} procesada correctamente.")

else:
    st.error("No se pudo cargar el archivo UI_CONGIF. Verifica el repositorio.")
