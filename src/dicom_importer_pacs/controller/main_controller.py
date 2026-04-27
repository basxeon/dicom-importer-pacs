from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from dicom_importer_pacs.config.settings import AppSettings, load_settings, save_settings
from dicom_importer_pacs.model.dicom_model import build_study_records, discover_dicom_files
from dicom_importer_pacs.model.entities import StudyRecord, TagOverrides
from dicom_importer_pacs.services.import_service import ImportOptions, ImportService
from dicom_importer_pacs.utils.drive_utils import list_cdrom_roots
from dicom_importer_pacs.view.main_window import MainWindow


class MainController:
    def __init__(self, view: MainWindow) -> None:
        self.view = view
        self.settings: AppSettings = load_settings()
        self.import_service = ImportService(self.settings)
        self.studies: list[StudyRecord] = []

    def initialize(self) -> None:
        self.view.apply_settings(self.settings)
        self.view.import_folder_clicked.connect(self.on_import_folder)
        self.view.import_dvd_clicked.connect(self.on_import_dvd)
        self.view.send_clicked.connect(self.on_send)
        self.view.save_config_clicked.connect(self.on_save_config)

    def _load_from_root(self, root: Path) -> None:
        try:
            self.view.log(f"Scanning: {root}")
            dicom_files = discover_dicom_files(root)
            studies_map = build_study_records(dicom_files)
            self.studies = list(studies_map.values())
            self.view.set_studies(self.studies)
            self.view.log(f"Loaded {len(dicom_files)} DICOM files in {len(self.studies)} studies")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self.view, "Import Error", str(exc))

    def on_import_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self.view, "Select DICOM Folder")
        if not folder:
            return
        self._load_from_root(Path(folder))

    def on_import_dvd(self) -> None:
        roots = list_cdrom_roots()
        if not roots:
            QMessageBox.warning(self.view, "DVD/CD", "No DVD/CD drive found")
            return
        self._load_from_root(roots[0])

    def on_save_config(self) -> None:
        self.settings = self.view.collect_settings()
        save_settings(self.settings)
        self.import_service = ImportService(self.settings)
        self.view.log("Configuration saved")

    def _on_progress(self, idx: int, total: int, message: str) -> None:
        self.view.update_progress(idx, total, message)

    def on_send(self) -> None:
        if not self.studies:
            QMessageBox.information(self.view, "No Data", "Please import DICOM studies first")
            return

        try:
            settings = self.view.collect_settings()
            self.settings = settings
            self.import_service = ImportService(self.settings)

            overrides_by_study = self.view.collect_overrides()
            options = ImportOptions(
                regenerate_uid=self.view.regenerate_uid_enabled(),
                demographic_mode=self.view.demographic_mode_enabled(),
            )

            self.import_service.import_to_pacs(
                self.studies,
                overrides_by_study,
                options,
                self._on_progress,
            )
            QMessageBox.information(self.view, "Done", "All studies sent to PACS")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self.view, "Send Error", str(exc))
