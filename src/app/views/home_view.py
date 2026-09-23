import flet as ft

from app.config.settings import APP_NAME


class HomeView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(APP_NAME, size=36, weight=ft.FontWeight.BOLD),
                    ft.Text("Analyse, extraction et conversion de sous-titres"),
                ],
            ),
        )
