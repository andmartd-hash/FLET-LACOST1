import flet as ft

def main(page: ft.Page):
    page.title = "Conversor de Datos - Andresma"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Componentes de la interfaz
    titulo = ft.Text("Bienvenido a tu Asistente de Sistemas", size=30, weight="bold")
    input_data = ft.TextField(label="Pega aquí los datos de Excel", multiline=True)
    
    def procesar_click(e):
        # Aquí iría la lógica para reemplazar tus macros
        page.add(ft.Text(f"Procesando: {input_data.value[:20]}..."))

    btn_procesar = ft.ElevatedButton("Procesar Datos", on_click=procesar_click)

    page.add(
        ft.Column(
            [titulo, input_data, btn_procesar],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    # Para despliegue web se usa view=ft.AppView.WEB_BROWSER
    ft.app(target=main)