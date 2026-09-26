import flet as ft

from app.config import theme
from app.models.tool_info import ToolInfo


class ToolStatusCard(ft.Container):
    def __init__(self, info: ToolInfo):
        super().__init__()
        status_color = theme.ACCENT if info.available else "#EF6C75"
        status_text = "Disponible" if info.available else "Introuvable"
        details = info.version or info.error or "Aucune information"

        self.padding = 16
        self.bgcolor = theme.SURFACE
        self.border = ft.Border.all(1, theme.BORDER)
        self.border_radius = 10
        self.content = ft.Column(
            spacing=6,
            controls=[
                ft.Row(controls=[
                    ft.Text(info.name.upper(), size=16, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED if info.available else ft.Icons.ERROR_ROUNDED,
                            color=status_color, size=18),
                    ft.Text(status_text, color=status_color),
                ]),
                ft.Text(details, color=theme.TEXT_MUTED, size=13),
                ft.Text(info.path or "Chemin non détecté", color=theme.TEXT_MUTED, size=12),
            ],
        )
