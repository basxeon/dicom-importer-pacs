from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from dicom_importer_pacs.controller.main_controller import MainController
from dicom_importer_pacs.view.main_window import MainWindow


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DICOM Importer PACS")

    window = MainWindow()
    controller = MainController(window)
    controller.initialize()

    window.show()
    sys.exit(app.exec())
