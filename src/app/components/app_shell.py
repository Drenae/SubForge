import flet as ft

from app.config import theme
from app.config.settings import APP_NAME


class AppShell(ft.Row):
    def __init__(self, content: ft.Control, on_navigate):
        self.content_area = ft.Container(expand=True, content=content)
        self._on_navigate = on_navigate
        self._routes = ("home", "extraction", "conversion")
        super().__init__(
            expand=True,
            spacing=0,
            controls=[self._build_rail(), self.content_area],
        )

    def _build_rail(self) -> ft.Container:
        self.rail = ft.NavigationRail(
            selected_index=0,
            extended=True,
            label_type=ft.NavigationRailLabelType.NONE,
            min_width=72,
            min_extended_width=220,
            bgcolor=theme.SURFACE,
            indicator_color=theme.ACCENT_SOFT,
            group_alignment=-1,
            leading=ft.Container(
                padding=ft.Padding.only(left=20, top=22, bottom=22),
                content=ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.SUBTITLES_ROUNDED, color=theme.ACCENT, size=28),
                    ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                ]),
            ),
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME_ROUNDED, label="Accueil"),
                ft.NavigationRailDestination(icon=ft.Icons.SAVE_ALT_ROUNDED, label="Extraction"),
                ft.NavigationRailDestination(icon=ft.Icons.AUTO_FIX_HIGH_ROUNDED, label="Conversion"),
            ],
            trailing=ft.Container(
                padding=ft.Padding.symmetric(horizontal=14, vertical=16),
                content=ft.Button("Paramètres", icon=ft.Icons.SETTINGS_ROUNDED,
                                  on_click=lambda _: self._on_navigate("settings")),
            ),
            pin_trailing_to_bottom=True,
            on_change=self._navigate,
        )
        return ft.Container(
            width=220,
            border=ft.Border(right=ft.BorderSide(1, theme.BORDER)),
            content=self.rail,
        )

    def _navigate(self, event):
        index = event.control.selected_index
        if index is not None and 0 <= index < len(self._routes):
            self._on_navigate(self._routes[index])

    def set_content(self, content: ft.Control, route: str) -> None:
        selected = self._routes.index(route) if route in self._routes else None
        if self.rail.selected_index != selected:
            self.rail.selected_index = selected
            self.rail.update()
        self.content_area.content = content
        self.content_area.update()
