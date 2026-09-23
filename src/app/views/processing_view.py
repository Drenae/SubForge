import flet as ft

from app.config import theme


class ProcessingView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(
                controls=[
                    ft.Text("Traitements", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text("Extraction, conversion et OCR seront regroupés ici.", color=theme.TEXT_MUTED),
                ]
            ),
        )
