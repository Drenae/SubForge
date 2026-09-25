from pathlib import Path

import flet as ft

from app.config import theme
from app.services.extraction_service import ExtractionJob
from app.services.ocr_service import OcrError, OcrService
from app.services.ocr_batch_service import OcrBatchService
from app.services.pgs_service import PgsError
from app.state.media_state import MediaState


class ConversionView(ft.Column):
    def __init__(self, state: MediaState):
        self.title = "Conversion"
        self.subtitle = "Convertissez des sous-titres PGS en SRT avec l'OCR intégré."
        self.actions = []
        self.state = state
        self.picker = ft.FilePicker()
        self.destination: Path | None = None
        self.cancel_requested = False
        self.ocr_running = False
        self.batch_running = False
        self.ocr_source: Path | None = None
        self.output_label = ft.Text("Aucun dossier de destination choisi", color=theme.TEXT_MUTED)
        self.ocr_status = ft.Text(color=theme.TEXT_MUTED)
        self.ocr_selection = ft.Text(color=theme.TEXT_MUTED)
        self.progress = ft.ProgressBar(value=0, color=theme.ACCENT)
        self.report = ft.ListView(expand=True, spacing=6)
        self.ocr_editor = ft.TextField(label="SRT reconnu (corrigez le texte avant l'enregistrement)",
                                       multiline=True, min_lines=8, max_lines=16, visible=False)
        self.ocr_save = ft.Button("Enregistrer le SRT corrigé", on_click=self._save_ocr, visible=False)
        super().__init__(
            expand=True,
            spacing=16,
            controls=[
                ft.Text("Fichier .sup isolé : choisissez le fichier, vérifiez le texte reconnu, puis enregistrez le SRT corrigé.",
                        color=theme.TEXT_MUTED),
                ft.Row(wrap=True, controls=[
                    ft.Button("Choisir un .sup et lancer l'OCR", on_click=self._run_ocr),
                    self.ocr_save,
                ]),
                ft.Text("Pistes sélectionnées dans Accueil : le traitement extrait temporairement chaque PGS "
                        "et enregistre directement son SRT dans le dossier choisi. Relisez ensuite les SRT produits.",
                        color=theme.TEXT_MUTED),
                self.ocr_selection,
                ft.Row(wrap=True, controls=[
                    ft.Button("Choisir le dossier de sortie", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=self._choose_folder),
                    ft.Button("Convertir les PGS sélectionnés en SRT", on_click=self._run_ocr_batch),
                    ft.Button("Annuler après la piste en cours", on_click=self._cancel),
                ]),
                self.output_label, self.progress, self.ocr_status, self.report, self.ocr_editor,
            ],
        )
        self.refresh_selection()

    def _safe_update(self):
        if self.page is not None:
            self.update()

    def _jobs(self) -> list[ExtractionJob]:
        return [ExtractionJob(media.path, track)
                for key, media in self.state.files.items()
                for track in self.state.tracks.get(key, [])
                if (key, track.index) in self.state.selected_tracks
                and track.codec.casefold() == "hdmv_pgs_subtitle"]

    def refresh_selection(self):
        self.ocr_selection.value = f"{len(self._jobs())} piste(s) PGS sélectionnée(s) pour l'OCR"

    async def _choose_folder(self, _):
        path = await self.picker.get_directory_path(dialog_title="Choisir le dossier de sortie des SRT")
        if path:
            self.destination = Path(path)
            self.output_label.value = str(self.destination)
            self._safe_update()

    def _cancel(self, _):
        if self.batch_running:
            self.cancel_requested = True
            self.ocr_status.value = "Arrêt demandé après la piste en cours…"
            self._safe_update()

    async def _run_ocr(self, _):
        if self.ocr_running or self.batch_running:
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
            cues = await OcrService.convert(self.ocr_source, progress)
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

    async def _run_ocr_batch(self, _):
        if self.batch_running or self.ocr_running:
            return
        jobs = [job for job in self._jobs() if job.track.codec.casefold() == "hdmv_pgs_subtitle"]
        if not jobs or self.destination is None:
            self.ocr_status.value = "Sélectionnez des pistes PGS dans Accueil et un dossier de sortie."
            self._safe_update()
            return
        self.batch_running = True
        self.cancel_requested = False
        self.report.controls = []
        self.progress.value = 0
        self.ocr_status.value = f"OCR par lot : 0/{len(jobs)} piste(s) terminée(s)."
        self._safe_update()

        def on_progress(done, total, count, result):
            if result is None:
                self.ocr_status.value = f"OCR {done + 1}/{total} · {count} sous-titre(s) reconnus."
            else:
                description = f"{result.job.source.name} · piste #{result.job.track.index}"
                if result.error:
                    self.report.controls.append(ft.Text(
                        f"Erreur OCR : {description} — {result.error}", color="#F28B82", selectable=True))
                else:
                    self.report.controls.append(ft.Text(
                        f"✓ {description} → {result.output.name} · {result.uncertain} à vérifier",
                        color=theme.TEXT, selectable=True))
                self.progress.value = done / total
                self.ocr_status.value = f"OCR par lot : {done}/{total} piste(s) terminée(s)."
            self._safe_update()

        try:
            results = await OcrBatchService.run(
                jobs, self.destination, lambda: self.cancel_requested, on_progress,
            )
            succeeded = sum(result.output is not None for result in results)
            uncertain = sum(result.uncertain for result in results)
            self.ocr_status.value = (
                f"OCR terminé : {succeeded} SRT créés, {len(results) - succeeded} erreur(s), "
                f"{len(jobs) - len(results)} non traitée(s) · {uncertain} sous-titre(s) à vérifier."
            )
        finally:
            self.batch_running = False
            self._safe_update()
