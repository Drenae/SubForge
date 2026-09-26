from collections.abc import Callable

import flet as ft

from app.components.nav_button import NavButton
from app.config import theme
from app.config.settings import APP_NAME


class AppNavigation(ft.Container):
    """Menu principal de SubForge."""

    def __init__(self, on_navigate: Callable[[str], None]):
        super().__init__(
            bgcolor=theme.BG,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.SUBTITLES_ROUNDED, color=ft.Colors.YELLOW_800, size=28),
                    ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                ]),
                ft.Container(width=16),
                NavButton("Accueil", ft.Icons.HOME_ROUNDED, "home", on_navigate),
                NavButton("Extraction", ft.Icons.SAVE_ALT_ROUNDED, "extraction", on_navigate),
                NavButton("Conversion", ft.Icons.AUTO_FIX_HIGH_ROUNDED, "conversion", on_navigate),
                ft.Container(expand=True),
                NavButton("Paramètres", ft.Icons.SETTINGS_ROUNDED, "settings", on_navigate),
            ]),
        )
