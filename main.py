import flet as ft
import pandas as pd
import os

def main(page: ft.Page):
    page.title = "IBM Pricing Tool - Andresma"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- 1. DETECCIÓN DINÁMICA DE ARCHIVOS ---
    archivos_en_carpeta = os.listdir('.')
    
    def buscar_archivo(keyword):
        for f in archivos_en_carpeta:
            if keyword.lower() in f.lower() and f.endswith('.csv'):
                return f
        return None

    # Intentamos cargar los DataFrames de forma segura
    try:
        path_countries = buscar_archivo('countries')
        path_ui = buscar_archivo('UI_CONGIF') # Buscamos tu archivo de configuración
        path_risk = buscar_archivo('risk')

        if not path_countries or not path_ui:
            page.add(ft.Text(f"ERROR: No se encontraron los archivos necesarios.\nArchivos detectados: {archivos_en_carpeta}", color="red", weight="bold"))
            return

        # Carga efectiva de datos
        df_countries = pd.read_csv(path_countries)
        df_ui = pd.read_csv(path_ui)
        df_risk = pd.read_csv(path_risk) if path_risk else pd.DataFrame()

    except Exception as e:
        page.add(ft.Text(f"Error crítico al leer CSV: {e}", color="red"))
        return

    # --- 2. VARIABLES Y COMPONENTES ---
    # Extraemos países (columnas desde la índice 2 según tu archivo)
    lista_paises = df_countries.columns[2:].tolist()
    
    dd_paises = ft.Dropdown(
        label="Seleccionar País (IBM Region)",
        options=[ft.dropdown.Option(p) for p in lista_paises],
        width=300
    )

    txt_er = ft.TextField(label="Exchange Rate (ER)", read_only=True, width=150)
    
    def cambio_pais(e):
        try:
            # En tu CSV, la fila 1 (índice 1) contiene los valores de ER
            valor_er = df_countries.loc[1, dd_paises.value]
            txt_er.value = str(valor_er)
            page.update()
        except Exception as ex:
            print(f"Error al obtener ER: {ex}")

    dd_paises.on_change = cambio_pais

    # --- 3. DISEÑO DE LA INTERFAZ ---
    page.add(
        ft.Column([
            ft.Text("HERRAMIENTA DE COTIZACIÓN - IBM LOGIC", size=25, weight="bold"),
            ft.Text(f"Configuración cargada desde: {path_ui}", size=12, italic=True),
            ft.Divider(),
            ft.Row([dd_paises, txt_er]),
            ft.Divider(),
            ft.Text("Módulos detectados en UI_CONGIF:", size=15, weight="bold"),
            ft.Text(f"Campos: {', '.join(df_ui.iloc[:, 0].dropna().unique()[:5])}...")
        ])
    )

if __name__ == "__main__":
    import os
    # Forzamos que corra en el puerto que GitHub espera
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
