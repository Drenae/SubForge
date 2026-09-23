import flet as ft

from app.config import theme


class SettingsView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(
                controls=[
                    ft.Text("Paramètres", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text("Les dépendances et préférences de SubForge seront configurées ici.", color=theme.TEXT_MUTED),
                ]
            ),
        )
