import flet as ft

from app.layout.app_header import AppHeader
from app.layout.app_navigation import AppNavigation


class AppShell(ft.Column):
    def __init__(self, content: ft.Control, on_navigate):
        super().__init__()
        self.content_area = ft.Container(
            expand=True, content=content,
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
        )
        self.header_area = ft.Container(content=self._app_header(content))
        self._on_navigate = on_navigate
        self.expand = True
        self.spacing = 0
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.controls = [
            AppNavigation(self._on_navigate),
            self.header_area,
            self.content_area,
        ]

    @staticmethod
    def _app_header(content: ft.Control) -> AppHeader:
        return AppHeader(content.title, content.subtitle, content.actions,
                         icon=content.header_icon)

    def set_content(self, content: ft.Control) -> None:
        self.header_area.content = self._app_header(content)
        self.content_area.content = content
        self.update()
