import flet as ft
import pandas as pd
import os

def main(page: ft.Page):
    page.title = "IBM Pricing Tool - Andresma"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- 1. DETECCIÓN DINÁMICA DE ARCHIVOS ---
    # Esto busca cualquier archivo que contenga la palabra clave en su nombre
    archivos = os.listdir('.')
    
    def buscar_archivo(keyword):
        for f in archivos:
            if keyword.lower() in f.lower() and f.endswith('.csv'):
                return f
        return None

    # Intentamos cargar los dataframes
    try:
        file_countries = buscar_archivo('countries')
        file_risk = buscar_archivo('risk')
        file_ui = buscar_archivo('UI_CONGIF') # Nota: puse CONGIF por tu nombre de archivo

        if not file_countries or not file_ui:
            page.add(ft.Text(f"ERROR: No se encontró el archivo de países o configuración en: {archivos}", color="red"))
            return

        df_countries = pd.read_csv(file_countries)
        df_ui = pd.read_csv(file_ui)
        df_risk = pd.read_csv(file_risk) if file_risk else pd.DataFrame()

    except Exception as e:
        page.add(ft.Text(f"Error crítico de lectura: {e}", color="red"))
        return

    # --- 2. COMPONENTES BASADOS EN TU ESTRUCTURA ---
    # Extraemos la lista de países (columnas desde la 3ra en adelante según tu CSV)
    lista_paises = df_countries.columns[2:].tolist()
    
    dd_paises = ft.Dropdown(
        label="Seleccionar País (IBM Region)",
        options=[ft.dropdown.Option(p) for p in lista_paises],
        width=300
    )

    txt_er = ft.TextField(label="Exchange Rate (ER)", read_only=True, width=150)
    
    def cambio_pais(e):
        # Según tu archivo, la fila 1 contiene el ER
        # .loc[1] accede a la segunda fila (índice 1)
        valor_er = df_countries.loc[1, dd_paises.value]
        txt_er.value = str(valor_er)
        page.update()

    dd_paises.on_change = cambio_pais

    # --- 3. DISEÑO DE LA PÁGINA ---
    page.add(
        ft.Column([
            ft.Text("CONFIGURACIÓN DE COTIZACIÓN", size=25, weight="bold"),
            ft.Row([dd_paises, txt_er]),
            ft.Divider(),
            ft.Text("Estructura detectada de UI_CONGIF:", size=15, italic=True),
            ft.Text(f"Campos principales: {', '.join(df_ui.columns[:5])}...")
        ])
    )

if __name__ == "__main__":
    # Forzamos puerto 8080 para Codespaces
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)
