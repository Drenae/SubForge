import flet as ft

from app.app import SubForgeApp


def main(page: ft.Page) -> None:
    SubForgeApp(page).run()


if __name__ == "__main__":
    ft.run(main)
