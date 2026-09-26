import flet as ft


class AppHeader(ft.Container):
    """En-tête partagé : titre, sous-titre et actions à droite."""

    def __init__(self, title: str, subtitle: str, actions: list[ft.Control] | None = None):
        super().__init__(
            border=ft.Border(bottom=ft.BorderSide(2, ft.Colors.YELLOW_600)),
            padding=ft.Padding.symmetric(horizontal=24, vertical=18),
            bgcolor=ft.Colors.YELLOW_800,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(title, size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        ft.Text(subtitle, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54),
                    ]),
                    *(actions or []),
                ],
            ),
        )
