import flet as ft

from app.config import theme


class PageHeader(ft.Row):
    """En-tête commun des pages, avec action principale facultative à droite."""

    def __init__(self, title: str, description: str, action: ft.Control | None = None):
        super().__init__(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(title, size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text(description, color=theme.TEXT_MUTED),
                ]),
                *([action] if action is not None else []),
            ],
        )
