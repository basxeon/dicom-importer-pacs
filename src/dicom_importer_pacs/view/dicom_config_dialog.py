from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from dicom_importer_pacs.config.settings import AppSettings


class DicomConfigDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("DICOM Configuration")
        self.setModal(True)
        self.resize(500, 250)

        self.max_name_len = QLineEdit(str(settings.max_name_len))
        self.max_acc_len = QLineEdit(str(settings.max_accession_len))
        self.max_desc_len = QLineEdit(str(settings.max_study_desc_len))

        form = QFormLayout()
        form.addRow("Max Patient Name Length", self.max_name_len)
        form.addRow("Max Accession Length", self.max_acc_len)
        form.addRow("Max Study Description Length", self.max_desc_len)

        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        button_layout = QVBoxLayout()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(button_layout)

        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            """
            QDialog {
                background: #f6f9fc;
            }
            QLabel {
                color: #1b2a41;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #b8c7d9;
                border-radius: 6px;
                padding: 6px;
                color: #1b2a41;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
            QPushButton {
                background: #134074;
                color: #ffffff;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #0b2545;
            }
            """
        )

    def get_settings(self) -> tuple[int, int, int]:
        try:
            max_name_len = int(self.max_name_len.text())
            max_acc_len = int(self.max_acc_len.text())
            max_desc_len = int(self.max_desc_len.text())
        except ValueError as exc:
            raise ValueError("Max lengths must be integers") from exc

        return (max_name_len, max_acc_len, max_desc_len)
