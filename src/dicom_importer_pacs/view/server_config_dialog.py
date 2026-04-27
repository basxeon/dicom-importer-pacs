from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from dicom_importer_pacs.config.settings import AeConfig, AppSettings


class ServerConfigDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Server Configuration")
        self.setModal(True)
        self.resize(500, 300)

        self.local_ae = QLineEdit(settings.ae.local_ae_title)
        self.remote_ae = QLineEdit(settings.ae.pacs_ae_title)
        self.remote_host = QLineEdit(settings.ae.pacs_host)
        self.remote_port = QLineEdit(str(settings.ae.pacs_port))
        self.max_name_len = QLineEdit(str(settings.max_name_len))
        self.max_acc_len = QLineEdit(str(settings.max_accession_len))
        self.max_desc_len = QLineEdit(str(settings.max_study_desc_len))

        form = QFormLayout()
        form.addRow("Local AE Title", self.local_ae)
        form.addRow("PACS AE Title", self.remote_ae)
        form.addRow("PACS Host", self.remote_host)
        form.addRow("PACS Port", self.remote_port)
        form.addRow("Max Patient Name Len", self.max_name_len)
        form.addRow("Max Accession Len", self.max_acc_len)
        form.addRow("Max Study Desc Len", self.max_desc_len)

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
            QLineEdit {
                background: #ffffff;
                border: 1px solid #b8c7d9;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background: #134074;
                color: #ffffff;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0b2545;
            }
            """
        )

    def get_settings(self) -> AppSettings:
        try:
            port = int(self.remote_port.text())
            max_name_len = int(self.max_name_len.text())
            max_acc_len = int(self.max_acc_len.text())
            max_desc_len = int(self.max_desc_len.text())
        except ValueError as exc:
            raise ValueError("Port and max lengths must be integers") from exc

        return AppSettings(
            ae=AeConfig(
                local_ae_title=self.local_ae.text().strip() or "DICOMIMPORTER",
                pacs_ae_title=self.remote_ae.text().strip() or "PACS",
                pacs_host=self.remote_host.text().strip() or "127.0.0.1",
                pacs_port=port,
            ),
            max_name_len=max_name_len,
            max_accession_len=max_acc_len,
            max_study_desc_len=max_desc_len,
        )
