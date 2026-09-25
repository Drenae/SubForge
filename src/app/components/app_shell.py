import flet as ft

from app.config import theme
from app.config.settings import APP_NAME
from app.components.page_header import PageHeader


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
            border=ft.Border(bottom=ft.BorderSide(1, theme.BORDER)),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.SUBTITLES_ROUNDED, color=ft.Colors.YELLOW_800, size=28),
                    ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                ]),
                ft.Container(width=16),
                self._nav_button("Accueil", ft.Icons.HOME_ROUNDED, "home"),
                self._nav_button("Extraction", ft.Icons.SAVE_ALT_ROUNDED, "extraction"),
                self._nav_button("Conversion", ft.Icons.AUTO_FIX_HIGH_ROUNDED, "conversion"),
                ft.Container(expand=True),
                self._nav_button("Paramètres", ft.Icons.SETTINGS_ROUNDED, "settings"),
            ]),
        )

    def _nav_button(self, label: str, icon: str, route: str) -> ft.Button:
        return ft.Button(
            content=ft.Row(controls=[
                ft.Icon(icon, size=20, color=ft.Colors.BLACK),
                ft.Text(label, color=ft.Colors.BLACK),
            ]),
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=12, vertical=14),
                shape=ft.RoundedRectangleBorder(radius=6),
                side={
                    ft.ControlState.DEFAULT: ft.BorderSide(2, ft.Colors.YELLOW_800),
                    ft.ControlState.HOVERED: ft.BorderSide(2, ft.Colors.YELLOW_800)
                },
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.YELLOW_700,
                    ft.ControlState.HOVERED: ft.Colors.YELLOW_800,
                },
            ),
            on_click=lambda _: self._on_navigate(route),
        )

    def set_content(self, content: ft.Control) -> None:
        self.header_area.content = self._page_header(content)
        self.content_area.content = content
        self.update()
