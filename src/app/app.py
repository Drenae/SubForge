import flet as ft

from app.layout.app_shell import AppShell
from app.config import theme
from app.config.settings import (
    APP_NAME,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_WIDTH,
)
from app.state.media_state import MediaState
from app.views.home_view import HomeView
from app.views.extraction_view import ExtractionView
from app.views.conversion_view import ConversionView
from app.views.settings_view import SettingsView


class SubForgeApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.media_state = MediaState()
        self.extraction_view = ExtractionView(self.media_state)
        self.conversion_view = ConversionView(self.media_state)
        self.shell = AppShell(HomeView(self.media_state), self.navigate)

    def run(self) -> None:
        self._configure_page()
        self.page.add(self.shell)

    def _configure_page(self) -> None:
        self.page.title = APP_NAME
        self.page.padding = 0
        self.page.bgcolor = theme.BG
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = theme.build_theme()
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.min_width = WINDOW_MIN_WIDTH
        self.page.window.min_height = WINDOW_MIN_HEIGHT
        self.page.window.maximized = True

    def navigate(self, route: str) -> None:
        if route == "extraction":
            self.extraction_view.refresh_selection()
            content = self.extraction_view
        elif route == "conversion":
            self.conversion_view.refresh_selection()
            content = self.conversion_view
        elif route == "settings":
            content = SettingsView()
        else:
            content = HomeView(self.media_state)
        self.shell.set_content(content)
