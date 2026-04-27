from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dicom_importer_pacs.config.settings import AppSettings
from dicom_importer_pacs.model.entities import StudyRecord, TagOverrides


class MainWindow(QMainWindow):
    import_dvd_clicked = Signal()
    import_folder_clicked = Signal()
    send_clicked = Signal()
    server_config_clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DICOM Importer to PACS")
        self.resize(1366, 860)

        # Setup menu bar with File and Server menus
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)
        
        file_menu = menubar.addMenu("File")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        server_menu = menubar.addMenu("Server")
        config_action = server_menu.addAction("Server Config...")
        config_action.triggered.connect(self.server_config_clicked.emit)

        root = QWidget()
        self.setCentralWidget(root)

        self.title_label = QLabel("DICOM Importer PACS")
        self.title_label.setObjectName("Title")
        self.subtitle = QLabel("Import from DVD/CD or folder, inspect tags, edit metadata, and send via C-STORE")
        self.subtitle.setObjectName("Subtitle")

        self.btn_import_dvd = QPushButton("Import from DVD Drive")
        self.btn_import_folder = QPushButton("Import from Folder")
        self.btn_send = QPushButton("Send to PACS")

        self.chk_regen_uid = QCheckBox("Regenerate Study/Series/SOP UIDs")
        self.chk_demo_mode = QCheckBox("Patient Demography Mode (anonymize selected fields)")

        self.studies_table = QTableWidget(0, 8)
        self.studies_table.setHorizontalHeaderLabels(
            [
                "Study UID",
                "Patient ID",
                "Patient Name",
                "Accession",
                "Study Description",
                "Files",
                "Edit Preview",
                "Tag Check",
            ]
        )
        self.studies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.studies_table.verticalHeader().setVisible(False)

        self.progress = QProgressBar()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        self._build_layout(root)
        self._wire_events()
        self._apply_modern_style()

    def _build_layout(self, root: QWidget) -> None:
        main = QVBoxLayout(root)
        header = QVBoxLayout()
        header.addWidget(self.title_label)
        header.addWidget(self.subtitle)

        action_row = QHBoxLayout()
        action_row.addWidget(self.btn_import_dvd)
        action_row.addWidget(self.btn_import_folder)
        action_row.addWidget(self.btn_send)
        action_row.addStretch()

        options_card = QFrame()
        options_card.setObjectName("Card")
        options_layout = QVBoxLayout(options_card)
        options_layout.addWidget(self.chk_regen_uid)
        options_layout.addWidget(self.chk_demo_mode)
        options_layout.addStretch()

        main.addLayout(header)
        main.addLayout(action_row)
        main.addWidget(options_card)
        main.addWidget(self.studies_table)
        main.addWidget(self.progress)
        main.addWidget(self.log_box)

    def _wire_events(self) -> None:
        self.btn_import_dvd.clicked.connect(self.import_dvd_clicked.emit)
        self.btn_import_folder.clicked.connect(self.import_folder_clicked.emit)
        self.btn_send.clicked.connect(self.send_clicked.emit)

    def _apply_modern_style(self) -> None:
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f6f9fc, stop:1 #e7eef7);
            }
            QLabel#Title {
                font-size: 26px;
                font-weight: 700;
                color: #1b2a41;
            }
            QLabel#Subtitle {
                color: #36526b;
                margin-bottom: 10px;
            }
            QFrame#Card, QGroupBox {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid #c8d6e5;
                border-radius: 14px;
                padding: 10px;
            }
            QGroupBox {
                font-weight: 600;
                color: #1b2a41;
            }
            QPushButton {
                background: #134074;
                color: #ffffff;
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0b2545;
            }
            QLineEdit, QPlainTextEdit, QTableWidget {
                background: #ffffff;
                border: 1px solid #b8c7d9;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #a9bcd0;
                border-radius: 8px;
                text-align: center;
                background: #f4f7fb;
                min-height: 24px;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: #3f88c5;
            }
            """
        )

    def apply_settings(self, settings: AppSettings) -> None:
        pass

    def collect_settings(self) -> AppSettings:
        from dicom_importer_pacs.config.settings import load_settings
        return load_settings()

    def set_studies(self, studies: list[StudyRecord]) -> None:
        self.studies_table.setRowCount(len(studies))
        for row, study in enumerate(studies):
            self.studies_table.setItem(row, 0, QTableWidgetItem(study.study_instance_uid))
            self.studies_table.setItem(row, 1, QTableWidgetItem(study.patient_id))
            self.studies_table.setItem(row, 2, QTableWidgetItem(study.patient_name))
            self.studies_table.setItem(row, 3, QTableWidgetItem(study.accession_number))
            self.studies_table.setItem(row, 4, QTableWidgetItem(study.study_description))
            self.studies_table.setItem(row, 5, QTableWidgetItem(str(len(study.file_paths))))
            self.studies_table.setItem(row, 6, QTableWidgetItem("Editable"))
            self.studies_table.setItem(row, 7, QTableWidgetItem("OK"))

    def collect_overrides(self) -> dict[str, TagOverrides]:
        overrides: dict[str, TagOverrides] = {}
        for row in range(self.studies_table.rowCount()):
            uid_item = self.studies_table.item(row, 0)
            if uid_item is None:
                continue
            uid = uid_item.text()
            overrides[uid] = TagOverrides(
                patient_id=(self.studies_table.item(row, 1).text() if self.studies_table.item(row, 1) else ""),
                patient_name=(self.studies_table.item(row, 2).text() if self.studies_table.item(row, 2) else ""),
                accession_number=(self.studies_table.item(row, 3).text() if self.studies_table.item(row, 3) else ""),
                study_description=(self.studies_table.item(row, 4).text() if self.studies_table.item(row, 4) else ""),
            )
        return overrides

    def update_progress(self, idx: int, total: int, message: str) -> None:
        if total <= 0:
            self.progress.setValue(0)
            return
        value = int((idx / total) * 100)
        self.progress.setValue(value)
        self.log(message)

    def log(self, message: str) -> None:
        self.log_box.appendPlainText(message)

    def regenerate_uid_enabled(self) -> bool:
        return self.chk_regen_uid.isChecked()

    def demographic_mode_enabled(self) -> bool:
        return self.chk_demo_mode.isChecked()
