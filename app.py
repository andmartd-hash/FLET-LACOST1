import streamlit as st
import pandas as pd
import os

# Configuración de apariencia profesional
st.set_page_config(page_title="IBM Pricing & Quote Tool", layout="wide")

# CSS personalizado para mejorar el diseño
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; background: white; }
    [data-testid="stHeader"] { background: #0066cc; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    files = os.listdir('.')
    def find_file(key): 
        return next((f for f in files if key.lower() in f.lower() and f.endswith('.csv')), None)
    
    # Mapeo según tus archivos cargados
    dfs = {
        'ui': find_file('UI_CONGIF'),
        'countries': find_file('countries'),
        'risk': find_file('risk'),
        'offering': find_file('offering'),
        'lplat': find_file('lplat'),
        'lband': find_file('lband'),
        'slc': find_file('slc')
    }
    
    loaded = {}
    for key, path in dfs.items():
        if path:
            df = pd.read_csv(path)
            # LIMPIEZA CRÍTICA: Elimina espacios en blanco en nombres de columnas
            df.columns = df.columns.str.strip()
            loaded[key] = df
    return loaded

data = load_data()

if 'ui' in data:
    st.title("💼 IBM Service & Pricing Engine")
    
    # --- BARRA LATERAL (Siguiendo UI_CONFIG Secciones 1-4) ---
    with st.sidebar:
        st.header("Configuración")
        id_cot = st.text_input("ID Cotización", value="COT-001")
        
        # Selección de País y ER
        paises = data['countries'].columns[2:].tolist()
        pais_sel = st.selectbox("País", options=paises)
        moneda = st.radio("Currency", ["USD", "Local"])
        
        # Fila 1 del CSV countries contiene el ER
        er_val = float(data['countries'].loc[1, pais_sel]) if moneda == "Local" else 1.0
        st.metric("Exchange Rate", f"{er_val:,.4f}")
        
        riesgo = st.selectbox("QA Risk", options=data['risk']['Risk'].tolist())
        contingencia = float(data['risk'][data['risk']['Risk'] == riesgo]['Contingency'].iloc[0])

    # --- PESTAÑAS PARA MEJORAR LA APARIENCIA ---
    tab_serv, tab_labor = st.tabs(["📦 Módulo Servicios", "👥 Módulo Management"])

    with tab_serv:
        st.subheader("Configuración de Servicios e Infraestructura")
        c1, c2, c3 = st.columns(3)
        with c1:
            customer = st.text_input("Customer Name")
            offering = st.selectbox("Offering", options=data['offering']['Offering'].tolist())
        with c2:
            qty = st.number_input("QTY", min_value=1, value=1)
            slc = st.selectbox("SLC", options=data['slc']['SLC'].tolist())
        with c3:
            unit_cost = st.number_input("Unit Cost USD", min_value=0.0, step=0.01)
            duration = st.number_input("Duration (Months)", min_value=1, value=12)

    with tab_labor:
        st.subheader("Cálculo de Labor / Management")
        m1, m2 = st.columns(2)
        with m1:
            mcbr = st.radio("MachCat / BandRate", ["Machine Category", "Brand Rate Full"], horizontal=True)
        with m2:
            df_labor = data['lplat'] if "Machine" in mcbr else data['lband']
            cat_labor = st.selectbox("MC / RR", options=df_labor['MC/RR'].unique().tolist())

    # --- CÁLCULOS FINALES (Búsqueda Segura) ---
    row_labor = df_labor[df_labor['MC/RR'] == cat_labor]
    costo_mensual = float(row_labor[pais_sel].iloc[0]) if not row_labor.empty else 0.0

    total_service = (unit_cost * duration * qty) * (1 + contingencia)
    total_manage = (costo_mensual * duration)
    
    st.divider()
    
    # Dashboard de Resultados
    res1, res2, res3 = st.columns(3)
    res1.metric("Total Service", f"${total_service:,.2f}")
    res2.metric("Total Manage", f"${total_manage:,.2f}")
    res3.metric("TOTAL COTIZACIÓN", f"${(total_service + total_manage):,.2f}", delta="USD")

    if st.button("💾 Guardar y Validar"):
        st.balloons()
        st.success(f"Cotización {id_cot} generada exitosamente.")
else:
    st.error("Archivo UI_CONGIF no detectado. Revisa los nombres en GitHub.")
