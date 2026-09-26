import flet as ft

class AppHeaderButton(ft.Button):
    def __init__(self, text=None, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.content = ft.Text(text, size=16)
        self.color = ft.Colors.WHITE
        self.icon = ft.Icon(icon, size=30)
        self.icon_color = ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            shape=ft.RoundedRectangleBorder(radius=6),
            side={ft.ControlState.DEFAULT: ft.BorderSide(2, ft.Colors.BLACK_54)},
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLACK_12,
                ft.ControlState.HOVERED: ft.Colors.BLACK_54
            }
        )
