from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pydicom import dcmread
from pydicom.dataset import Dataset

from dicom_importer_pacs.config.settings import AppSettings
from dicom_importer_pacs.model.dicom_model import (
    apply_tag_overrides,
    copy_to_buffer,
    regenerate_uids,
)
from dicom_importer_pacs.model.entities import StudyRecord, TagOverrides
from dicom_importer_pacs.services.pacs_sender import PacsConnection, PacsSender


@dataclass(slots=True)
class ImportOptions:
    regenerate_uid: bool = False
    demographic_mode: bool = False


class ImportService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def _prepare_datasets(
        self,
        studies: list[StudyRecord],
        overrides_by_study: dict[str, TagOverrides],
        options: ImportOptions,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[Dataset]:
        all_files = [path for study in studies for path in study.file_paths]
        with tempfile.TemporaryDirectory(prefix="dicom-buffer-") as temp_dir:
            buffered_files = copy_to_buffer(all_files, Path(temp_dir), progress_callback)
            datasets: list[Dataset] = []
            total = len(buffered_files)
            for idx, file_path in enumerate(buffered_files, start=1):
                ds = dcmread(file_path, force=True)
                study_uid = str(getattr(ds, "StudyInstanceUID", ""))
                overrides = overrides_by_study.get(study_uid, TagOverrides())

                ds = apply_tag_overrides(
                    ds,
                    overrides,
                    self.settings.max_name_len,
                    self.settings.max_accession_len,
                    self.settings.max_study_desc_len,
                )

                if options.demographic_mode:
                    ds.PatientBirthDate = ""
                    ds.PatientAddress = ""
                    ds.OtherPatientIDs = ""

                if options.regenerate_uid:
                    ds = regenerate_uids(ds)

                datasets.append(ds)
                if progress_callback:
                    progress_callback(idx, total, f"Prepared {file_path.name}")

            return datasets

    def import_to_pacs(
        self,
        studies: list[StudyRecord],
        overrides_by_study: dict[str, TagOverrides],
        options: ImportOptions,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> None:
        datasets = self._prepare_datasets(studies, overrides_by_study, options, progress_callback)
        pacs = PacsSender(
            PacsConnection(
                local_ae_title=self.settings.ae.local_ae_title,
                remote_ae_title=self.settings.ae.pacs_ae_title,
                remote_host=self.settings.ae.pacs_host,
                remote_port=self.settings.ae.pacs_port,
            )
        )
        pacs.send(datasets, progress_callback)
