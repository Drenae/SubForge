import flet as ft


class AppButton(ft.Button):
    """Bouton commun pour les actions de l'application hors navigation."""

    def __init__(self, label: str | None = None, *, icon: str | None = None, **kwargs):
        content = ft.Text(label, color=ft.Colors.BLACK) if label is not None else None
        icon_control = ft.Icon(icon, size=20, color=ft.Colors.BLACK) if icon is not None else None
        super().__init__(content=content, icon=icon_control, **kwargs)
        self.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=12, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=6),
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.GREY_500),
                ft.ControlState.HOVERED: ft.BorderSide(1, ft.Colors.GREY_600),
            },
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.WHITE_70,
                ft.ControlState.HOVERED: ft.Colors.WHITE,
            },
        )
