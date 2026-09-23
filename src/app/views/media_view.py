import flet as ft

from app.config import theme


class MediaView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(
                controls=[
                    ft.Text("Médias", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text("L'import et l'analyse des fichiers seront disponibles ici.", color=theme.TEXT_MUTED),
                ]
            ),
        )
