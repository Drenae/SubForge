import flet as ft

from app.config import theme
from app.state.media_state import MediaState


class MediaView(ft.Container):
    def __init__(self, state: MediaState):
        self.state = state
        self.picker = ft.FilePicker()
        self.status = ft.Text(color=theme.TEXT_MUTED, selectable=True)
        self.file_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.count = ft.Text(color=theme.TEXT_MUTED)
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(
                expand=True,
                spacing=18,
                controls=[
                    ft.Text("Médias", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.Text("Importez les vidéos dont vous souhaitez analyser les sous-titres.", color=theme.TEXT_MUTED),
                    ft.Row(controls=[
                        ft.Button("Ajouter des vidéos", icon=ft.Icons.ADD_ROUNDED, on_click=self._pick_files),
                        ft.Button("Tout retirer", icon=ft.Icons.DELETE_OUTLINE_ROUNDED, on_click=self._clear),
                    ]),
                    self.status,
                    self.count,
                    self.file_list,
                ],
            ),
        )
        self._render()

    async def _pick_files(self, _):
        selected = await self.picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["mkv", "mp4", "m4v", "mov", "avi", "webm", "ts", "m2ts"],
        )
        if not selected:
            return
        paths = [item.path for item in selected if item.path]
        missing = len(selected) - len(paths)
        added, errors = self.state.add(paths)
        if missing:
            errors.append(f"{missing} fichier(s) sans chemin local accessible")
        self.status.value = f"{added} vidéo(s) ajoutée(s)." + ("\n" + "\n".join(errors) if errors else "")
        self._render()
        self.update()

    def _remove(self, path: str):
        self.state.remove(path)
        self.status.value = "Vidéo retirée."
        self._render()
        self.update()

    def _clear(self, _):
        self.state.clear()
        self.status.value = "Sélection vidée."
        self._render()
        self.update()

    def _render(self):
        files = list(self.state.files.values())
        self.count.value = f"{len(files)} vidéo(s) chargée(s)"
        self.file_list.controls = [
            ft.Container(
                bgcolor=theme.SURFACE,
                border=ft.Border.all(1, theme.BORDER),
                border_radius=8,
                padding=12,
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.MOVIE_ROUNDED, color=theme.ACCENT),
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(media.name, color=theme.TEXT, weight=ft.FontWeight.W_600),
                        ft.Text(str(media.path), color=theme.TEXT_MUTED, size=12, selectable=True),
                    ]),
                    ft.Text(f"{media.size / 1024 / 1024:.1f} Mo", color=theme.TEXT_MUTED),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, tooltip="Retirer", on_click=lambda _, p=str(media.path): self._remove(p)),
                ]),
            ) for media in files
        ]
