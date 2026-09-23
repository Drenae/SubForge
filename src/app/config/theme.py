import flet as ft

BG = "#0B1118"
SURFACE = "#111A24"
SURFACE_ALT = "#162230"
BORDER = "#223247"
TEXT = "#EAF2F8"
TEXT_MUTED = "#8FA3B8"
ACCENT = "#2EC4B6"
ACCENT_SOFT = "#153B3A"


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ACCENT,
            surface=SURFACE,
            on_surface=TEXT,
        ),
        font_family="Segoe UI",
    )
