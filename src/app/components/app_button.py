import flet as ft

class AppButton(ft.Button):
    def __init__(self, text=None, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.content = ft.Text(text)
        self.color = ft.Colors.BLACK
        self.icon = ft.Icon(icon, size=20)
        self.icon_color = ft.Colors.BLACK
        self.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=12, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=6),
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.GREY_500),
                ft.ControlState.HOVERED: ft.BorderSide(1, ft.Colors.GREY_600)
            },
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.GREY_500,
                ft.ControlState.HOVERED: ft.Colors.GREY_100
            }
        )
