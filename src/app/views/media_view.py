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
        self.file_list = ft.ListView(spacing=8, expand=True)
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
                    ft.Row(controls=[
                        ft.Button("Tout sélectionner", on_click=lambda _: self._select_all(True)),
                        ft.Button("Tout désélectionner", on_click=lambda _: self._select_all(False)),
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
                        self.state.set_tracks(key, tracks)
                except FFprobeError as exc:
                    if key in self.state.files:
                        self.state.set_tracks(key, [])
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

    def _select_all(self, selected: bool):
        self.state.select_all(selected)
        self._render()
        self.update()

    def _toggle_track(self, key: str, index: int, selected: bool):
        self.state.select_track(key, index, selected)
        self._update_count()
        self.count.update()

    def _update_count(self):
        self.count.value = (f"{len(self.state.files)} vidéo(s) chargée(s) · "
                            f"{len(self.state.selected_tracks)} piste(s) sélectionnée(s)")

    def _render(self):
        self._update_count()
        self.file_list.controls = [self._media_tile(media) for media in self.state.files.values()]

    def _media_tile(self, media):
        key = str(media.path).casefold()
        tracks = self.state.tracks.get(key)
        if key in self.state.analysis_errors:
            children = [ft.Text(self.state.analysis_errors[key], color="#F28B82", size=12)]
        elif tracks is None:
            children = [ft.Text("En attente d'analyse", color=theme.TEXT_MUTED, size=12)]
        elif not tracks:
            children = [ft.Text("Aucune piste de sous-titres", color=theme.TEXT_MUTED, size=12)]
        else:
            children = [self._track_row(key, track) for track in tracks]
        return ft.Container(
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=8,
            content=ft.ExpansionTile(
                title=ft.Row(controls=[
                    ft.Icon(ft.Icons.MOVIE_ROUNDED, color=theme.ACCENT),
                    ft.Text(media.name, color=theme.TEXT, weight=ft.FontWeight.W_600, expand=True),
                    ft.Text(f"{len(tracks) if tracks is not None else '—'} piste(s)", color=theme.TEXT_MUTED),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, tooltip="Retirer",
                                  on_click=lambda _, p=str(media.path): self._remove(p)),
                ]),
                subtitle=ft.Text(str(media.path), color=theme.TEXT_MUTED, size=12, selectable=True),
                controls=[ft.Container(padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                                       content=ft.Column(controls=children, spacing=5))],
            ),
        )

    def _track_row(self, key, track):
        label = (f"#{track.index}  ·  {track.language or 'Langue inconnue'}  ·  {track.codec}"
                 + (f"  ·  {track.title}" if track.title else "")
                 + ("  ·  FORCED" if track.forced else "")
                 + ("  ·  DEFAULT" if track.default else ""))
        return ft.Container(
            bgcolor=theme.ACCENT_SOFT if track.forced else theme.SURFACE_ALT,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=10, vertical=3),
            content=ft.Checkbox(
                label=label, value=(key, track.index) in self.state.selected_tracks,
                active_color=theme.ACCENT,
                on_change=lambda e, k=key, i=track.index: self._toggle_track(k, i, bool(e.control.value)),
            ),
        )
