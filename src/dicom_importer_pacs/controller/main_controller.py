from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from dicom_importer_pacs.config.settings import AppSettings, load_settings, save_settings
from dicom_importer_pacs.model.dicom_model import build_study_records, discover_dicom_files
from dicom_importer_pacs.model.entities import StudyRecord, TagOverrides
from dicom_importer_pacs.services.import_service import ImportOptions, ImportService
from dicom_importer_pacs.utils.drive_utils import list_cdrom_roots
from dicom_importer_pacs.view.main_window import MainWindow
from dicom_importer_pacs.view.server_config_dialog import ServerConfigDialog
from dicom_importer_pacs.view.dicom_config_dialog import DicomConfigDialog


class MainController:
    def __init__(self, view: MainWindow) -> None:
        self.view = view
        self.settings: AppSettings = load_settings()
        self.import_service = ImportService(self.settings)
        self.studies: list[StudyRecord] = []

    def _show_message(self, icon: QMessageBox.Icon, title: str, text: str) -> None:
        msg = QMessageBox(self.view)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet(
            """
            QMessageBox {
                background: #f6f9fc;
            }
            QMessageBox QLabel {
                color: #1b2a41;
                font-size: 13px;
                min-width: 260px;
            }
            QMessageBox QPushButton {
                background: #134074;
                color: #ffffff;
                border-radius: 8px;
                padding: 6px 12px;
                min-width: 72px;
                font-weight: 600;
            }
            QMessageBox QPushButton:hover {
                background: #0b2545;
            }
            """
        )
        msg.exec()

    def _show_info(self, title: str, text: str) -> None:
        self._show_message(QMessageBox.Icon.Information, title, text)

    def _show_warning(self, title: str, text: str) -> None:
        self._show_message(QMessageBox.Icon.Warning, title, text)

    def _show_error(self, title: str, text: str) -> None:
        self._show_message(QMessageBox.Icon.Critical, title, text)

    def initialize(self) -> None:
        self.view.apply_settings(self.settings)
        self.view.import_folder_clicked.connect(self.on_import_folder)
        self.view.import_dvd_clicked.connect(self.on_import_dvd)
        self.view.send_clicked.connect(self.on_send)
        self.view.server_config_clicked.connect(self.on_server_config)
        self.view.dicom_config_clicked.connect(self.on_dicom_config)

    def _load_from_root(self, root: Path) -> None:
        try:
            self.view.log(f"Scanning: {root}")
            dicom_files = discover_dicom_files(root)
            studies_map = build_study_records(dicom_files)
            self.studies = list(studies_map.values())
            self.view.set_studies(self.studies)
            self.view.log(f"Loaded {len(dicom_files)} DICOM files in {len(self.studies)} studies")
        except Exception as exc:  # noqa: BLE001
            self._show_error("Import Error", str(exc))

    def on_import_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self.view, "Select DICOM Folder")
        if not folder:
            return
        self._load_from_root(Path(folder))

    def on_import_dvd(self) -> None:
        roots = list_cdrom_roots()
        if not roots:
            self._show_warning("DVD/CD", "No DVD/CD drive found")
            return
        self._load_from_root(roots[0])

    def on_server_config(self) -> None:
        dialog = ServerConfigDialog(self.settings, self.view)
        if dialog.exec() == QDialog.Accepted:
            ae = dialog.get_settings()
            self.settings.ae = ae
            save_settings(self.settings)
            self.import_service = ImportService(self.settings)
            self.view.log("Server configuration saved")

    def on_dicom_config(self) -> None:
        dialog = DicomConfigDialog(self.settings, self.view)
        if dialog.exec() == QDialog.Accepted:
            max_name_len, max_acc_len, max_desc_len = dialog.get_settings()
            self.settings.max_name_len = max_name_len
            self.settings.max_accession_len = max_acc_len
            self.settings.max_study_desc_len = max_desc_len
            save_settings(self.settings)
            self.import_service = ImportService(self.settings)
            self.view.log("DICOM configuration saved")

    def _on_progress(self, idx: int, total: int, message: str) -> None:
        self.view.update_progress(idx, total, message)

    def on_send(self) -> None:
        if not self.studies:
            self._show_info("No Data", "Please import DICOM studies first")
            return

        try:
            options = ImportOptions(
                regenerate_uid=self.view.regenerate_uid_enabled(),
                demographic_mode=self.view.demographic_mode_enabled(),
            )

            overrides_by_study = self.view.collect_overrides()
            self.import_service.import_to_pacs(
                self.studies,
                overrides_by_study,
                options,
                self._on_progress,
            )
            self._show_info("Done", "All studies sent to PACS")
        except Exception as exc:  # noqa: BLE001
            self._show_error("Send Error", str(exc))
