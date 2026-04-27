# DICOM Importer PACS (Python, MVC)

A desktop tool for importing DICOM files from DVD/CD or folders, reviewing and editing key DICOM tags, then sending to PACS using C-STORE.

## Main Features

- Import from DVD/CD drive and folder.
- Copy files to local buffer one-by-one before reading DICOM data (safer for optical media).
- Edit base DICOM tags before send:
  - `PatientID` (HN)
  - `PatientName`
  - `AccessionNumber`
  - `StudyDescription`
- Multi-study send to PACS in one run.
- Demography mode for anonymizing selected patient fields.
- UID regeneration to avoid UID collision in PACS.
- Basic tag preview/edit grid before sending.
- AE Title configuration for local app and PACS server.
- C-STORE with transfer syntax requests including:
  - Implicit/Explicit VR Little Endian
  - JPEG Lossless
  - JPEG 2000 (lossless/lossy)

## Architecture (MVC)

- `model`: DICOM file discovery, grouping, tag sanitation/override, UID regeneration.
- `view`: PySide6 modern UI.
- `controller`: Connects user events to services and handles app flow.
- `services`: Import pipeline and PACS C-STORE sender.
- `config`: AE/PACS settings persistence.

## Project Structure

```text
src/dicom_importer_pacs/
  app.py
  config/settings.py
  controller/main_controller.py
  model/entities.py
  model/dicom_model.py
  services/import_service.py
  services/pacs_sender.py
  utils/drive_utils.py
  view/main_window.py
main.py
tests/test_dicom_model.py
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Unit Test

```bash
pytest -q
```

## Debug Plan

1. Unit tests on model/services for tag processing and buffer copy.
2. Integration test with test PACS (Orthanc/DCM4CHEE).
3. Add mock sender to test C-STORE error handling.
4. Verify large DVD media with interrupted read scenarios.
5. Add structured logs with study/file identifiers.

## Exception Handling

- File scan/import/send are wrapped in explicit try/except in controller.
- PACS association and C-STORE errors raise `PacsSenderError`.
- Invalid config values trigger friendly UI warnings.

## Suggested Next Enhancements

- Background worker thread (`QThread`) for non-blocking UI while sending large studies.
- Full DICOM tag inspector dialog with search/filter.
- Rule engine for PACS DB constraints (auto-trim/replace restricted chars by site policy).
- Retry policy for flaky optical media and PACS network interruptions.
- Detailed send report export (CSV/PDF).
