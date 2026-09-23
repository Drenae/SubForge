import flet as ft

from app.config import theme
from app.config.settings import APP_NAME


class HomeView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(APP_NAME, size=34, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text(
                        "Analyse, extraction et conversion de sous-titres",
                        size=16,
                        color=theme.TEXT_MUTED,
                    ),
                    ft.Container(height=18),
                    ft.Container(
                        padding=24,
                        bgcolor=theme.SURFACE,
                        border=ft.Border.all(1, theme.BORDER),
                        border_radius=12,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.VIDEO_FILE_ROUNDED, size=38, color=theme.ACCENT),
                                ft.Text("Aucun média chargé", size=18, weight=ft.FontWeight.W_600, color=theme.TEXT),
                                ft.Text("L'import des fichiers MKV arrivera dans la prochaine phase.", color=theme.TEXT_MUTED),
                            ],
                        ),
                    ),
                ],
            ),
        )
