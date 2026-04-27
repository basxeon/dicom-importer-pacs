from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.misc import is_dicom
from pydicom.uid import generate_uid

from dicom_importer_pacs.model.entities import StudyRecord, TagOverrides


def discover_dicom_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        # Skip DICOMDIR and hidden files
        if path.is_file() and path.name.upper() != "DICOMDIR" and not path.name.startswith("."):
            if is_dicom(path):
                files.append(path)
    return files


def build_study_records(paths: list[Path]) -> dict[str, StudyRecord]:
    studies: dict[str, StudyRecord] = {}
    for path in paths:
        ds = dcmread(path, stop_before_pixels=True, force=True)
        study_uid = str(getattr(ds, "StudyInstanceUID", "UNKNOWN"))
        if study_uid not in studies:
            studies[study_uid] = StudyRecord(
                study_instance_uid=study_uid,
                accession_number=str(getattr(ds, "AccessionNumber", "")),
                patient_id=str(getattr(ds, "PatientID", "")),
                patient_name=str(getattr(ds, "PatientName", "")),
                study_description=str(getattr(ds, "StudyDescription", "")),
                file_paths=[],
            )
        studies[study_uid].file_paths.append(path)
    return studies


def copy_to_buffer(
    source_files: list[Path],
    buffer_dir: Path,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> list[Path]:
    buffer_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    total = len(source_files)
    for idx, src in enumerate(source_files, start=1):
        dst = buffer_dir / f"{idx:06d}_{src.name}"
        # Copy one by one to avoid direct read issues from optical media.
        shutil.copy2(src, dst)
        copied.append(dst)
        if progress_callback:
            progress_callback(idx, total, f"Buffered {src.name}")

    return copied


def sanitize_for_pacs(value: str, max_len: int) -> str:
    cleaned = " ".join(value.strip().split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[:max_len]


def apply_tag_overrides(
    dataset: Dataset,
    overrides: TagOverrides,
    max_name_len: int,
    max_accession_len: int,
    max_study_desc_len: int,
) -> Dataset:
    if overrides.patient_id:
        dataset.PatientID = sanitize_for_pacs(overrides.patient_id, 64)
    if overrides.patient_name:
        dataset.PatientName = sanitize_for_pacs(overrides.patient_name, max_name_len)
    if overrides.accession_number:
        dataset.AccessionNumber = sanitize_for_pacs(
            overrides.accession_number,
            max_accession_len,
        )
    if overrides.study_description:
        dataset.StudyDescription = sanitize_for_pacs(
            overrides.study_description,
            max_study_desc_len,
        )
    return dataset


def regenerate_uids(dataset: Dataset) -> Dataset:
    dataset.StudyInstanceUID = generate_uid()
    dataset.SeriesInstanceUID = generate_uid()
    dataset.SOPInstanceUID = generate_uid()
    if hasattr(dataset, "file_meta") and dataset.file_meta is not None:
        dataset.file_meta.MediaStorageSOPInstanceUID = dataset.SOPInstanceUID
    return dataset
