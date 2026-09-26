from collections.abc import Callable

import flet as ft


class AppNavigationButton(ft.Button):
    def __init__(self, text=None, icon=None, route=str, on_navigate= Callable[[str], None], **kwargs):
        super().__init__(**kwargs)
        self.content = ft.Text(text)
        self.color = ft.Colors.BLACK
        self.icon = ft.Icon(icon, size=24)
        self.icon_color = ft.Colors.BLACK
        self.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=12, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=6),
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(2, ft.Colors.YELLOW_800)
            },
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.AMBER,
                ft.ControlState.HOVERED: ft.Colors.AMBER_100,
            },
        )
        self.on_click = lambda _: on_navigate(route)
