import asyncio
from pathlib import Path

import flet as ft

from app.config import theme
from app.services.extraction_service import ExtractionJob, ExtractionService
from app.services.ocr_service import OcrError, OcrService
from app.services.pgs_service import PgsError
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
        self.file_progress = ft.ProgressBar(value=0, color=theme.ACCENT)
        self.report = ft.ListView(expand=True, spacing=6)
        self.ocr_running = False
        self.ocr_source: Path | None = None
        self.ocr_language = ft.Dropdown(label="Langue OCR", value="fra", width=150,
            options=[ft.DropdownOption(key=code, text=label) for code, label in
                     (("fra", "Français"), ("eng", "Anglais"), ("deu", "Allemand"), ("spa", "Espagnol"))])
        self.ocr_status = ft.Text(color=theme.TEXT_MUTED)
        self.ocr_editor = ft.TextField(label="SRT reconnu (corrigez le texte avant l'enregistrement)",
                                       multiline=True, min_lines=8, max_lines=16, visible=False)
        self.ocr_save = ft.Button("Enregistrer le SRT corrigé", on_click=self._save_ocr, visible=False)
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
                self.output_label, self.summary, self.progress, self.file_progress, self.report,
                ft.Text("OCR PGS → SRT", size=18, color=theme.TEXT),
                ft.Row(wrap=True, controls=[self.ocr_language,
                    ft.Button("Choisir un .sup et lancer l'OCR", on_click=self._run_ocr),
                    self.ocr_save]),
                self.ocr_status, self.ocr_editor,
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
        self.file_progress.value = 0
        self._safe_update()

        def on_progress(done, total, result):
            self.progress.value = done / total
            self.file_progress.value = 1
            description = f"{result.job.source.name} · piste #{result.job.track.index}"
            if result.error:
                self.report.controls.append(ft.Text(f"Erreur : {description} — {result.error}", color="#F28B82", selectable=True))
            else:
                self.report.controls.append(ft.Text(f"✓ {description} → {result.output.name}", color=theme.TEXT, selectable=True))
            self.summary.value = f"{done}/{total} piste(s) traitée(s)"
            self._safe_update()

        def on_partial(done, total, fraction):
            self.file_progress.value = fraction
            self.progress.value = (done + fraction) / total if fraction is not None else done / total
            self.summary.value = f"{done}/{total} piste(s) terminée(s) · piste en cours"
            self._safe_update()

        try:
            results = await ExtractionService.run_batch(
                jobs, self.destination, lambda: self.cancel_requested, on_progress, on_partial,
            )
            succeeded = sum(result.output is not None for result in results)
            failed = len(results) - succeeded
            remaining = len(jobs) - len(results)
            self.summary.value = f"Terminé : {succeeded} réussie(s), {failed} erreur(s), {remaining} non traitée(s)."
        finally:
            self.running = False
            self._safe_update()

    async def _run_ocr(self, _):
        if self.ocr_running:
            return
        selected = await self.picker.pick_files(
            allow_multiple=False, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["sup"])
        if not selected or not selected[0].path:
            return
        self.ocr_source = Path(selected[0].path)
        self.ocr_running = True
        self.ocr_editor.visible = False
        self.ocr_save.visible = False
        self.ocr_status.value = "Décodage PGS et reconnaissance en cours…"
        self._safe_update()

        def progress(count):
            self.ocr_status.value = f"{count} sous-titre(s) reconnus…"
            self._safe_update()

        try:
            cues = await OcrService.convert(self.ocr_source, self.ocr_language.value or "fra", progress)
            self.ocr_editor.value = OcrService.to_srt(cues)
            self.ocr_editor.visible = True
            self.ocr_save.visible = True
            uncertain = sum(cue.confidence is None or cue.confidence < 65 or not cue.text for cue in cues)
            self.ocr_status.value = (f"{len(cues)} sous-titre(s) reconnus · {uncertain} à vérifier "
                                     "(confiance faible ou texte vide). Corrigez le SRT avant de l'enregistrer.")
        except (OcrError, PgsError, OSError, ValueError) as exc:
            self.ocr_status.value = f"Erreur OCR : {exc}"
        finally:
            self.ocr_running = False
            self._safe_update()

    async def _save_ocr(self, _):
        if not self.ocr_editor.visible or not self.ocr_source:
            return
        path = await self.picker.save_file(
            dialog_title="Enregistrer le SRT corrigé",
            file_name=self.ocr_source.stem + ".srt",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["srt"],
        )
        if not path:
            return
        output = Path(path)
        if output.suffix.casefold() != ".srt":
            output = output.with_suffix(".srt")
        try:
            with output.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(self.ocr_editor.value or "")
            self.ocr_status.value = f"SRT enregistré : {output}"
        except FileExistsError:
            self.ocr_status.value = "Ce fichier existe déjà. Choisissez un autre nom."
        except OSError as exc:
            self.ocr_status.value = f"Enregistrement impossible : {exc}"
        self._safe_update()
