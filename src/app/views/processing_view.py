import asyncio
from pathlib import Path

import flet as ft

from app.config import theme
from app.services.extraction_service import ExtractionJob, ExtractionService
from app.state.media_state import MediaState


class ProcessingView(ft.Container):
    def __init__(self, state: MediaState):
        self.state = state
        self.picker = ft.FilePicker()
        self.destination: Path | None = None
        self.running = False
        self.cancel_requested = False
        self.output_label = ft.Text("Aucun dossier de destination choisi", color=theme.TEXT_MUTED)
        self.summary = ft.Text(color=theme.TEXT_MUTED)
        self.progress = ft.ProgressBar(value=0, color=theme.ACCENT)
        self.report = ft.ListView(expand=True, spacing=6)
        super().__init__(
            expand=True,
            padding=32,
            content=ft.Column(expand=True, spacing=16, controls=[
                ft.Text("Traitements", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                ft.Text("Extraction des pistes sélectionnées dans leur format original.", color=theme.TEXT_MUTED),
                ft.Row(wrap=True, controls=[
                    ft.Button("Choisir le dossier de sortie", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=self._choose_folder),
                    ft.Button("Extraire", icon=ft.Icons.SAVE_ALT_ROUNDED, on_click=self._extract),
                    ft.Button("Annuler après la piste en cours", on_click=self._cancel),
                ]),
                self.output_label, self.summary, self.progress, self.report,
            ]),
        )
        self._refresh_summary()

    def _safe_update(self):
        if self.page is not None:
            self.update()

    def _jobs(self) -> list[ExtractionJob]:
        return [ExtractionJob(media.path, track)
                for key, media in self.state.files.items()
                for track in self.state.tracks.get(key, [])
                if (key, track.index) in self.state.selected_tracks]

    def _refresh_summary(self):
        self.summary.value = f"{len(self._jobs())} piste(s) sélectionnée(s) pour extraction"

    async def _choose_folder(self, _):
        path = await self.picker.get_directory_path(dialog_title="Choisir le dossier de sortie")
        if path:
            self.destination = Path(path)
            self.output_label.value = str(self.destination)
            self._safe_update()

    def _cancel(self, _):
        if self.running:
            self.cancel_requested = True
            self.summary.value = "Arrêt demandé après la piste en cours…"
            self._safe_update()

    async def _extract(self, _):
        if self.running:
            return
        jobs = self._jobs()
        if not jobs or self.destination is None:
            self.summary.value = "Sélectionnez des pistes dans Médias et un dossier de sortie."
            self._safe_update()
            return
        self.running = True
        self.cancel_requested = False
        self.report.controls = []
        self.progress.value = 0
        self._safe_update()

        def on_progress(done, total, result):
            self.progress.value = done / total
            description = f"{result.job.source.name} · piste #{result.job.track.index}"
            if result.error:
                self.report.controls.append(ft.Text(f"Erreur : {description} — {result.error}", color="#F28B82", selectable=True))
            else:
                self.report.controls.append(ft.Text(f"✓ {description} → {result.output.name}", color=theme.TEXT, selectable=True))
            self.summary.value = f"{done}/{total} piste(s) traitée(s)"
            self._safe_update()

        try:
            results = await ExtractionService.run_batch(
                jobs, self.destination, lambda: self.cancel_requested, on_progress,
            )
            succeeded = sum(result.output is not None for result in results)
            failed = len(results) - succeeded
            remaining = len(jobs) - len(results)
            self.summary.value = f"Terminé : {succeeded} réussie(s), {failed} erreur(s), {remaining} non traitée(s)."
        finally:
            self.running = False
            self._safe_update()
