import flet as ft

from app.config import theme
from app.config.settings import APP_NAME
from app.components.page_header import PageHeader
from app.components.nav_button import NavButton


class AppShell(ft.Column):
    def __init__(self, content: ft.Control, on_navigate):
        self.content_area = ft.Container(
            expand=True, content=content,
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
        )
        self.header_area = ft.Container(content=self._page_header(content))
        self._on_navigate = on_navigate
        super().__init__(
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._build_menu(),
                self.header_area,
                self.content_area,
            ],
        )

    @staticmethod
    def _page_header(content: ft.Control) -> PageHeader:
        return PageHeader(content.title, content.subtitle, content.actions)

    def _build_menu(self) -> ft.Container:
        return ft.Container(
            bgcolor=theme.BG,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.SUBTITLES_ROUNDED, color=ft.Colors.YELLOW_800, size=28),
                    ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                ]),
                ft.Container(width=16),
                NavButton("Accueil", ft.Icons.HOME_ROUNDED, "home", self._on_navigate),
                NavButton("Extraction", ft.Icons.SAVE_ALT_ROUNDED, "extraction", self._on_navigate),
                NavButton("Conversion", ft.Icons.AUTO_FIX_HIGH_ROUNDED, "conversion", self._on_navigate),
                ft.Container(expand=True),
                NavButton("Paramètres", ft.Icons.SETTINGS_ROUNDED, "settings", self._on_navigate),
            ]),
        )

    def set_content(self, content: ft.Control) -> None:
        self.header_area.content = self._page_header(content)
        self.content_area.content = content
        self.update()
