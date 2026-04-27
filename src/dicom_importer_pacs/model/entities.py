from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class TagOverrides:
    patient_id: str = ""
    patient_name: str = ""
    accession_number: str = ""
    study_description: str = ""


@dataclass(slots=True)
class DicomFileRecord:
    source_path: Path
    buffered_path: Path | None = None
    study_instance_uid: str = ""
    series_instance_uid: str = ""
    sop_instance_uid: str = ""
    modality: str = ""


@dataclass(slots=True)
class StudyRecord:
    study_instance_uid: str
    accession_number: str
    patient_id: str
    patient_name: str
    study_description: str
    file_paths: list[Path] = field(default_factory=list)
