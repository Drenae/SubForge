import flet as ft

from app.config.settings import (
    APP_NAME,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_WIDTH,
)
from app.views.home_view import HomeView


class SubForgeApp:
    def __init__(self, page: ft.Page):
        self.page = page

    def run(self) -> None:
        self._configure_page()
        self.page.add(HomeView())

    def _configure_page(self) -> None:
        self.page.title = APP_NAME
        self.page.padding = 0
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.min_width = WINDOW_MIN_WIDTH
        self.page.window.min_height = WINDOW_MIN_HEIGHT
