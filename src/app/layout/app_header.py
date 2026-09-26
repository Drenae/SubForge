import flet as ft


class AppHeader(ft.Container):
    """En-tête partagé : titre, sous-titre et actions à droite."""

    def __init__(self, title: str, subtitle: str, actions: list[ft.Control] | None = None,
                 icon: str | None = None):
        super().__init__()
        self.border = ft.Border(top=ft.BorderSide(2, ft.Colors.AMBER_700), bottom=ft.BorderSide(2, ft.Colors.AMBER_700))
        self.padding = ft.Padding.symmetric(horizontal=24, vertical=18)
        self.bgcolor = ft.Colors.AMBER
        self.content = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                *([ft.Icon(icon, size=50, color=ft.Colors.BLACK)] if icon is not None else []),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(title, size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    ft.Text(subtitle, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54),
                ]),
                *(actions or []),
            ],
        )
