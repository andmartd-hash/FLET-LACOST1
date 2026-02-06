import flet as ft
import pandas as pd
import os

# --- FUNCIÓN DE CARGA SEGURA ---
def cargar_datos():
    # Buscamos los archivos reales en la carpeta para evitar errores de nombre
    archivos_presentes = os.listdir('.')
    
    # Mapeo de archivos basado en tus subidas
    files_map = {
        'countries': 'flet1-BASE.xlsx - countries.csv',
        'risk': 'flet1-BASE.xlsx - risk.csv',
        'offering': 'flet1-BASE.xlsx - offering.csv',
        'slc': 'flet1-BASE.xlsx - slc.csv',
        'lplat': 'flet1-BASE.xlsx - lplat.csv',
        'lband': 'flet1-BASE.xlsx - lband.csv',
        'ui': 'flet1-BASE.xlsx - UI_CONGIF.csv'
    }

    datos = {}
    for key, name in files_map.items():
        if name in archivos_presentes:
            datos[key] = pd.read_csv(name)
        else:
            # Si no lo encuentra, crea un DataFrame vacío para que no explote la App
            print(f"ALERTA: No se encontró {name}")
            datos[key] = pd.DataFrame()
    return datos

# Cargamos globalmente antes de que inicie la App
data = cargar_datos()

def main(page: ft.Page):
    page.title = "Cotizador Andresma - IBM"
    page.scroll = "adaptive"

    # Verificar si df_countries existe en nuestro diccionario de datos
    df_countries = data.get('countries', pd.DataFrame())

    if df_countries.empty:
        page.add(ft.Text("ERROR: No se cargaron los datos de países. Revisa los nombres de los archivos CSV.", color="red"))
        return

    # --- LÓGICA DE LA INTERFAZ ---
    lista_paises = df_countries.columns[2:].tolist() if not df_countries.empty else []
    
    dd_country = ft.Dropdown(
        label="Selecciona País",
        options=[ft.dropdown.Option(p) for p in lista_paises],
        width=300
    )

    def on_change_country(e):
        # Ejemplo: obtener el ER (Exchange Rate) de la fila 1
        try:
            er_val = df_countries.loc[1, dd_country.value]
            lbl_res.value = f"Exchange Rate para {dd_country.value}: {er_val}"
        except:
            lbl_res.value = "Error al obtener ER"
        page.update()

    dd_country.on_change = on_change_country
    lbl_res = ft.Text("Selecciona un país para ver la lógica de IBM")

    page.add(
        ft.Text("Configuración de Cotización", size=20, weight="bold"),
        dd_country,
        lbl_res
    )

if __name__ == "__main__":
    # Forzamos puerto 8080 para que GitHub lo detecte fácil
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)
