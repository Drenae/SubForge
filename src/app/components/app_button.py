import flet as ft


class AppButton(ft.Button):
    """Bouton commun pour les actions de l'application hors navigation."""

    def __init__(self, label: str | None = None, *, icon: str | None = None, **kwargs):
        super().__init__(content=label, icon=icon, **kwargs)
