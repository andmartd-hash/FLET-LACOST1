import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IBM Pricing Tool", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS (IBM LOOK) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #f4f7f6; }
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #171717; color: white; }
    /* Métricas */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #0f62fe; /* IBM Blue */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 5px 5px 0 0;
        border: 1px solid #e0e0e0;
        color: #161616;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f62fe;
        color: white;
    }
    h1, h2, h3 { color: #161616; font-family: 'IBM Plex Sans', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ROBUSTA ---
@st.cache_data
def load_data():
    files = os.listdir('.')
    def get_csv(k): return next((f for f in files if k.lower() in f.lower() and f.endswith('.csv')), None)
    
    # Mapeo de archivos
    rutas = {
        'ui': get_csv('UI_CONGIF'),
        'countries': get_csv('countries'),
        'risk': get_csv('risk'),
        'offering': get_csv('offering'),
        'lplat': get_csv('lplat'),
        'lband': get_csv('lband'),
        'slc': get_csv('slc')
    }
    
    db = {}
    for key, path in rutas.items():
        if path:
            try:
                df = pd.read_csv(path)
                # LIMPIEZA TOTAL: Elimina espacios en nombres de columnas y strings
                df.columns = df.columns.str.strip()
                # Intenta limpiar espacios en celdas de texto
                obj_cols = df.select_dtypes(['object']).columns
                for c in obj_cols:
                    df[c] = df[c].str.strip()
                db[key] = df
            except Exception as e:
                st.error(f"Error leyendo {path}: {e}")
        else:
            db[key] = None
    return db

db = load_data()

# --- PROCESAMIENTO DE UI CONFIG ---
# Tu archivo UI tiene los campos en COLUMNAS. Vamos a transponerlo para iterar mejor.
# Asumimos que la columna 0 es 'name field' y contiene las claves ('section', 'source', etc.)
if db['ui'] is not None:
    # Transponer el DataFrame: Las columnas se vuelven índice
    df_ui_T = db['ui'].set_index(db['ui'].columns[0]).T
    # Ahora el índice son los Nombres de Campo (ID_Cotizacion, Countries, etc.)
    # Y las columnas son 'section', 'source', 'Logic rule', etc.
    df_ui_T.columns = df_ui_T.columns.str.strip() # Limpiar nombres de atributos
else:
    st.error("CRÍTICO: No se encontró UI_CONGIF.csv")
    st.stop()

# --- INTERFAZ DINÁMICA ---
st.title("💼 IBM Pricing & Quote Engine")

# Contenedores de datos para cálculos
inputs = {}

# 1. BARRA LATERAL (según UI_CONFIG)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=100)
    st.markdown("### Configuración Global")
    
    # Filtramos campos que van en 'barra lateral izquierda'
    campos_sidebar = df_ui_T[df_ui_T['section'].str.contains('barra lateral', case=False, na=False)]
    
    for campo, row in campos_sidebar.iterrows():
        tipo_source = str(row.get('source', '')).lower()
        label = campo
        
        # Lógica específica por campo
        if 'countries' in label or 'countries' in tipo_source:
            opts = db['countries'].columns[2:].tolist() if db['countries'] is not None else []
            inputs['Country'] = st.selectbox("País / Country", options=opts)
        
        elif 'currency' in label.lower() or 'moneda' in tipo_source:
            inputs['Currency'] = st.radio("Moneda", ["USD", "Local"], horizontal=True)
            
        elif 'risk' in label.lower() or 'risk' in tipo_source:
            opts = db['risk']['Risk'].tolist() if db['risk'] is not None else []
            inputs['Risk'] = st.selectbox("QA Risk", options=opts)
            
        elif 'exchange rate' in label.lower() or 'countries er' in tipo_source:
            # Calculado automáticamente
            er = 1.0
            if inputs.get('Currency') == 'Local' and db['countries'] is not None:
                try:
                    pais = inputs.get('Country')
                    # Fila 1 es ER en countries.csv
                    er = float(db['countries'].loc[1, pais])
                except: pass
            inputs['ER'] = er
            st.metric("Exchange Rate (ER)", f"{er:,.4f}")
            
        elif 'consecutivo' in tipo_source or 'id_' in label.lower():
             inputs[label] = st.text_input(label, value="COT-2026-001")
             
        elif 'quote date' in label.lower():
            inputs[label] = st.date_input("Fecha Cotización", datetime.now())
            
        else:
            # Genérico
            inputs[label] = st.text_input(label)

# 2. ÁREA PRINCIPAL
tab1, tab2, tab3 = st.tabs(["📦 Servicios (Offering)", "⚙️ Management (Labor)", "💰 Resumen Financiero"])

with tab1:
    st.subheader("Detalle de Servicios")
    # Filtramos campos de 'modulo servicios'
    campos_serv = df_ui_T[df_ui_T['section'].str.contains('modulo servicios', case=False, na=False)]
    
    c1, c2, c3 = st.columns(3)
    cols_cycle = [c1, c2, c3]
    
    for i, (campo, row) in enumerate(campos_serv.iterrows()):
        col_actual = cols_cycle[i % 3]
        tipo_source = str(row.get('source', '')).lower()
        
        with col_actual:
            if 'offering' in label.lower() or 'offering' in tipo_source:
                opts = db['offering']['Offering'].tolist() if db['offering'] is not None else []
                inputs['Offering'] = st.selectbox(campo, options=opts)
                
            elif 'slc' in label.lower() or 'slc' in tipo_source:
                opts = db['slc']['SLC'].tolist() if db['slc'] is not None else []
                inputs['SLC'] = st.selectbox(campo, options=opts)
                
            elif 'qty' in label.lower():
                inputs['QTY'] = st.number_input(campo, min_value=1, value=1)
                
            elif 'duration' in label.lower():
                inputs['Duration'] = st.number_input(campo, min_value=1, value=12)
                
            elif 'cost usd' in label.lower() or 'unit cost' in label.lower():
                inputs['Unit Cost USD'] = st.number_input("Unit Cost (USD)", min_value=0.0, format="%.2f")
                
            elif 'date' in label.lower():
                inputs[campo] = st.date_input(campo)
                
            else:
                inputs[campo] = st.text_input(campo)

with tab2:
    st.subheader("Configuración de Labor")
    # Filtramos campos de 'modulo manag' o 'labor'
    campos_manag = df_ui_T[df_ui_T['section'].str.contains('manag|labor', case=False, na=False, regex=True)]
    
    c_m1, c_m2 = st.columns(2)
    
    # Radio Button Especial MCBR
    with c_m1:
        inputs['MCBR'] = st.radio("Criterio de Labor (MachCat / BandRate)", ["Machine Category", "Brand Rate Full"])
    
    with c_m2:
        # Lógica dinámica para cargar lista dependiendo de selección anterior
        df_labor = db['lplat'] if inputs['MCBR'] == "Machine Category" else db['lband']
        opts_labor = df_labor['MC/RR'].unique().tolist() if df_labor is not None else []
        inputs['MCRR_Selection'] = st.selectbox("Categoría / Banda (MC/RR)", options=opts_labor)

# --- CÁLCULOS (LOGIC ENGINE) ---
# Extraemos valores limpios para calcular
qty = inputs.get('QTY', 1)
duration = inputs.get('Duration', 12)
unit_cost_usd = inputs.get('Unit Cost USD', 0.0)
er = inputs.get('ER', 1.0)
pais = inputs.get('Country')

# Riesgo
risk_factor = 0.0
if db['risk'] is not None and 'Risk' in inputs:
    try:
        risk_row = db['risk'][db['risk']['Risk'] == inputs['Risk']]
        if not risk_row.empty:
            risk_factor = float(risk_row['Contingency'].iloc[0])
    except: pass

# Costo Labor
costo_labor_mensual = 0.0
if pais and inputs.get('MCRR_Selection'):
    df_labor_calc = db['lplat'] if inputs['MCBR'] == "Machine Category" else db['lband']
    try:
        # Búsqueda segura
        row = df_labor_calc[df_labor_calc['MC/RR'] == inputs['MCRR_Selection']]
        if not row.empty:
            costo_labor_mensual = float(row[pais].iloc[0])
    except Exception as e:
        st.warning(f"No se encontró costo de labor para {pais} en esa categoría.")

# Totales
total_service_usd = unit_cost_usd * duration * qty
total_service_local = total_service_usd * er
total_service_risk = total_service_usd * (1 + risk_factor)

total_manage_local = costo_labor_mensual * duration
# Si el costo labor viene en moneda local (asumido por tabla lplat/lband), lo convertimos a USD para el total o lo dejamos
# Asumiremos que la tabla lplat trae valores en Local Currency según tu excel.
total_manage_usd = total_manage_local / er if er > 0 else 0

grand_total_usd = total_service_risk + total_manage_usd

with tab3:
    st.subheader("Resultados de Cotización")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Costo Servicios (Base)", f"${total_service_usd:,.2f} USD", help="Unit Cost * Duration * QTY")
    m2.metric("Costo Management", f"${total_manage_usd:,.2f} USD", f"Local: {total_manage_local:,.2f}")
    m3.metric("Contingencia (Riesgo)", f"{risk_factor*100}%", f"${(total_service_usd * risk_factor):,.2f} USD")
    
    st.divider()
    st.markdown(f"<h2 style='text-align: center; color: #0f62fe;'>TOTAL: ${grand_total_usd:,.2f} USD</h2>", unsafe_allow_html=True)
    
    # Tabla de detalle
    st.write("### Desglose de Campos UI")
    st.json(inputs, expanded=False)

    if st.button("🚀 Generar PDF de Cotización", type="primary"):
        st.success("Cotización generada y lista para descargar.")
