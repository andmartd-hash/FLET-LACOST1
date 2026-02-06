import flet as ft
import pandas as pd
from datetime import datetime

# --- CARGA DE DATOS ---
# Cargamos los archivos que subiste para que la App sea dinámica
try:
    df_countries = pd.read_csv('flet1-BASE.xlsx - countries.csv')
    df_risk = pd.read_csv('flet1-BASE.xlsx - risk.csv')
    df_offering = pd.read_csv('flet1-BASE.xlsx - offering.csv')
    df_slc = pd.read_csv('flet1-BASE.xlsx - slc.csv')
    df_lplat = pd.read_csv('flet1-BASE.xlsx - lplat.csv')
    df_lband = pd.read_csv('flet1-BASE.xlsx - lband.csv')
except Exception as e:
    print(f"Error cargando archivos: {e}")

def main(page: ft.Page):
    page.title = "Cotizador Pro - Andresma IBM Edition"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 20

    # --- VARIABLES DE ESTADO ---
    lista_paises = df_countries.columns[2:].tolist() # De Argentina a Venezuela
    
    # --- COMPONENTES DE LA INTERFAZ ---
    
    # 1. Barra Lateral (Inputs de Configuración)
    txt_id_cot = ft.TextField(label="ID Cotización", value="COT-001", read_only=True, width=200)
    dd_country = ft.Dropdown(label="País", options=[ft.dropdown.Option(p) for p in lista_paises], width=200)
    dd_currency = ft.Dropdown(label="Moneda", options=[ft.dropdown.Option("USD"), ft.dropdown.Option("Local")], width=200)
    txt_er = ft.TextField(label="Exchange Rate", value="1.0", read_only=True, width=200)
    dd_risk = ft.Dropdown(label="QA Risk", options=[ft.dropdown.Option(r) for r in df_risk['Risk'].tolist()], width=200)
    
    txt_customer = ft.TextField(label="Customer Name", width=250)
    dd_offering = ft.Dropdown(label="Offering", options=[ft.dropdown.Option(o) for o in df_offering['Offering'].tolist()], width=400)
    
    # 2. Módulo de Servicios
    txt_qty = ft.TextField(label="QTY", value="1", width=100)
    dd_slc = ft.Dropdown(label="SLC", options=[ft.dropdown.Option(str(s)) for s in df_slc['SLC'].tolist()], width=200)
    txt_duration = ft.TextField(label="Duración (Meses)", value="12", width=120)
    txt_cost_usd = ft.TextField(label="Unit Cost USD", value="0", width=150)
    
    # 3. Módulo Manage (Cálculo de Labor/Plataforma)
    rb_mcbr = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="MC", label="Machine Category"),
        ft.Radio(value="BR", label="Band Rate")
    ]))
    dd_mcrr = ft.Dropdown(label="MC / RR", width=300)
    txt_monthly_cost = ft.TextField(label="Costo Mensual", read_only=True, width=150)
    
    # 4. Resultados
    lbl_total_service = ft.Text("Total Service: $0.00", size=20, weight="bold", color="blue")
    lbl_total_manage = ft.Text("Total Manage: $0.00", size=20, weight="bold", color="green")
    lbl_total_final = ft.Text("TOTAL COST: $0.00", size=30, weight="bold", color="orange")

    # --- LÓGICA DE NEGOCIO ---

    def update_er(e):
        if dd_country.value and dd_currency.value == "Local":
            # Busca el ER en la fila 1 del CSV de países para la columna seleccionada
            val = df_countries.loc[1, dd_country.value]
            txt_er.value = str(val)
        else:
            txt_er.value = "1.0"
        page.update()

    def update_mcrr_options(e):
        if rb_mcbr.value == "MC":
            dd_mcrr.options = [ft.dropdown.Option(str(x)) for x in df_lplat['MC/RR'].unique()]
        else:
            dd_mcrr.options = [ft.dropdown.Option(str(x)) for x in df_lband['MC/RR'].unique()]
        page.update()

    def calculate_totals(e):
        try:
            er = float(txt_er.value)
            qty = float(txt_qty.value)
            dur = float(txt_duration.value)
            cost_u = float(txt_cost_usd.value)
            
            # Cálculo Simple basado en tus reglas de Excel
            total_service = (cost_u * dur) * qty
            
            # Buscar costo mensual en tablas lplat/lband según país
            m_cost = 0
            if dd_country.value and dd_mcrr.value:
                df_source = df_lplat if rb_mcbr.value == "MC" else df_lband
                row = df_source[df_source['MC/RR'] == dd_mcrr.value]
                if not row.empty:
                    m_cost = float(row[dd_country.value].values[0])
            
            total_manage = m_cost * dur
            
            lbl_total_service.value = f"Total Service: ${total_service:,.2f}"
            lbl_total_manage.value = f"Total Manage: ${total_manage:,.2f}"
            lbl_total_final.value = f"TOTAL COST: ${(total_service + total_manage):,.2f}"
        except Exception as ex:
            print(f"Error en cálculo: {ex}")
        page.update()

    # Eventos
    dd_country.on_change = update_er
    dd_currency.on_change = update_er
    rb_mcbr.on_change = update_mcrr_options
    
    btn_calc = ft.ElevatedButton("Calcular Cotización", icon=ft.icons.CALCULATE, on_click=calculate_totals)

    # --- DISEÑO FINAL ---
    page.add(
        ft.Text("HERRAMIENTA DE COTIZACIÓN - IBM E/R LOGIC", size=25, weight="bold"),
        ft.Divider(),
        ft.Row([
            # Columna Configuración
            ft.Column([
                ft.Text("Configuración General", weight="bold"),
                txt_id_cot, dd_country, dd_currency, txt_er, dd_risk, txt_customer, dd_offering
            ], spacing=10),
            
            ft.VerticalDivider(width=1),
            
            # Columna Servicios y Labor
            ft.Column([
                ft.Text("Módulo de Servicios", weight="bold"),
                ft.Row([txt_qty, dd_slc, txt_duration]),
                txt_cost_usd,
                ft.Divider(),
                ft.Text("Módulo Management / Labor", weight="bold"),
                rb_mcbr,
                dd_mcrr,
                btn_calc,
                ft.Container(height=20),
                lbl_total_service,
                lbl_total_manage,
                lbl_total_final
            ], expand=True)
        ], vertical_alignment=ft.CrossAxisAlignment.START)
    )

if __name__ == "__main__":
    # Ejecución para Web en Codespaces
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
