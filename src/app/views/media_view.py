import asyncio

import flet as ft

from app.config import theme
from app.state.media_state import MediaState
from app.services.media_import_service import MediaImportService
from app.services.ffprobe_service import FFprobeService, FFprobeError


class MediaView(ft.Container):
    def __init__(self, state: MediaState):
        self.state = state
        self.picker = ft.FilePicker()
        self.status = ft.Text(color=theme.TEXT_MUTED, selectable=True)
        self.file_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.count = ft.Text(color=theme.TEXT_MUTED)
        self.analyzing = False
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
                        ft.Button("Importer un dossier", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=self._pick_folder),
                        ft.Button("Tout retirer", icon=ft.Icons.DELETE_OUTLINE_ROUNDED, on_click=self._clear),
                        ft.Button("Analyser les pistes", icon=ft.Icons.SUBTITLES_ROUNDED, on_click=self._analyze),
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

    async def _pick_folder(self, _):
        folder = await self.picker.get_directory_path(dialog_title="Choisir un dossier de vidéos")
        if not folder:
            return
        self.status.value = "Recherche des vidéos dans le dossier…"
        self.update()
        paths, errors = await asyncio.to_thread(MediaImportService.scan_folder, folder)
        added, rejected = await asyncio.to_thread(self.state.add, paths)
        errors.extend(rejected)
        self.status.value = (
            f"{added} vidéo(s) ajoutée(s) sur {len(paths)} trouvée(s)."
            + ("\n" + "\n".join(errors) if errors else "")
        )
        self._render()
        self.update()

    async def _analyze(self, _):
        if self.analyzing or not self.state.files:
            return
        self.analyzing = True
        files = list(self.state.files.values())
        try:
            for position, media in enumerate(files, 1):
                key = str(media.path).casefold()
                if key not in self.state.files:
                    continue
                self.status.value = f"Analyse {position}/{len(files)} : {media.name}"
                self.update()
                try:
                    tracks = await FFprobeService.analyze(media.path)
                    if key in self.state.files:
                        self.state.tracks[key] = tracks
                        self.state.analysis_errors.pop(key, None)
                except FFprobeError as exc:
                    if key in self.state.files:
                        self.state.tracks.pop(key, None)
                        self.state.analysis_errors[key] = str(exc)
                self._render()
                self.update()
            self.status.value = f"Analyse terminée : {len(files)} vidéo(s)."
            self.update()
        finally:
            self.analyzing = False

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
                        *self._track_labels(str(media.path).casefold()),
                    ]),
                    ft.Text(f"{media.size / 1024 / 1024:.1f} Mo", color=theme.TEXT_MUTED),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, tooltip="Retirer", on_click=lambda _, p=str(media.path): self._remove(p)),
                ]),
            ) for media in files
        ]

    def _track_labels(self, key: str) -> list[ft.Text]:
        if key in self.state.analysis_errors:
            return [ft.Text(self.state.analysis_errors[key], color="#F28B82", size=12)]
        if key not in self.state.tracks:
            return []
        tracks = self.state.tracks[key]
        if not tracks:
            return [ft.Text("Aucune piste de sous-titres", color=theme.TEXT_MUTED, size=12)]
        return [ft.Text(
            f"#{track.index} · {track.language or 'Langue inconnue'} · {track.codec}"
            + (f" · {track.title}" if track.title else "")
            + (" · Forced" if track.forced else "")
            + (" · Default" if track.default else ""),
            color=theme.ACCENT if track.forced else theme.TEXT_MUTED, size=12,
        ) for track in tracks]
