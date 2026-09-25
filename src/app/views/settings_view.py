import flet as ft

from app.components.tool_status_card import ToolStatusCard
from app.config import theme
from app.services.tool_detection_service import ToolDetectionService


class SettingsView(ft.Column):
    def __init__(self):
        self.title = "Paramètres"
        self.subtitle = "Vérifiez les outils utilisés par SubForge."
        self.actions = []
        self.tools_column = ft.Column(spacing=12)
        self.refresh_button = ft.Button(
            "Actualiser",
            icon=ft.Icons.REFRESH_ROUNDED,
            on_click=self._refresh_tools,
        )
        super().__init__(
            expand=True,
            spacing=18,
            controls=[
                    ft.Text("Outils multimédias", size=18, weight=ft.FontWeight.W_600, color=theme.TEXT),
                    ft.Text(
                        "SubForge utilise FFmpeg et FFprobe pour analyser et extraire les sous-titres. L’OCR est intégré.",
                        color=theme.TEXT_MUTED,
                    ),
                    self.refresh_button,
                    self.tools_column,
            ],
        )
        self._load_tools()

    def _load_tools(self) -> None:
        tools = ToolDetectionService.detect_all()
        self.tools_column.controls = [ToolStatusCard(info) for info in tools.values()]

    def _refresh_tools(self, _=None) -> None:
        self._load_tools()
        self.tools_column.update()
