from pathlib import Path

from pydicom.dataset import Dataset

from dicom_importer_pacs.model.dicom_model import (
    apply_tag_overrides,
    copy_to_buffer,
    regenerate_uids,
    sanitize_for_pacs,
)
from dicom_importer_pacs.model.entities import TagOverrides


def test_sanitize_for_pacs_truncates_long_text() -> None:
    result = sanitize_for_pacs("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 10)
    assert result == "ABCDEFGHIJ"


def test_apply_tag_overrides_updates_fields() -> None:
    ds = Dataset()
    overrides = TagOverrides(
        patient_id="HN001",
        patient_name="John  Doe",
        accession_number="ACC-123",
        study_description="CT Abdomen",
    )

    updated = apply_tag_overrides(ds, overrides, 64, 32, 64)

    assert updated.PatientID == "HN001"
    assert str(updated.PatientName) == "John Doe"
    assert updated.AccessionNumber == "ACC-123"
    assert updated.StudyDescription == "CT Abdomen"


def test_regenerate_uids_changes_uid_values() -> None:
    ds = Dataset()
    ds.StudyInstanceUID = "1.2.3.4"
    ds.SeriesInstanceUID = "1.2.3.5"
    ds.SOPInstanceUID = "1.2.3.6"

    updated = regenerate_uids(ds)

    assert updated.StudyInstanceUID != "1.2.3.4"
    assert updated.SeriesInstanceUID != "1.2.3.5"
    assert updated.SOPInstanceUID != "1.2.3.6"


def test_copy_to_buffer_copies_files_one_by_one(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    f1 = source_dir / "file1.dcm"
    f2 = source_dir / "file2.dcm"
    f1.write_bytes(b"abc")
    f2.write_bytes(b"def")

    buffer_dir = tmp_path / "buffer"
    copied = copy_to_buffer([f1, f2], buffer_dir)

    assert len(copied) == 2
    assert copied[0].exists()
    assert copied[1].exists()
    assert copied[0].read_bytes() == b"abc"
    assert copied[1].read_bytes() == b"def"
