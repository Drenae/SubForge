from collections.abc import Callable

import flet as ft


class NavButton(ft.Button):
    def __init__(self, label: str, icon: str, route: str,
                 on_navigate: Callable[[str], None]):
        super().__init__(
            content=ft.Row(controls=[
                ft.Icon(icon, size=20, color=ft.Colors.BLACK),
                ft.Text(label, color=ft.Colors.BLACK),
            ]),
        )
        self.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=12, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=6),
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(2, ft.Colors.YELLOW_800),
                ft.ControlState.HOVERED: ft.BorderSide(2, ft.Colors.YELLOW_800),
            },
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.YELLOW_700,
                ft.ControlState.HOVERED: ft.Colors.YELLOW_800,
            },
        )
        self.on_click = lambda _: on_navigate(route)
