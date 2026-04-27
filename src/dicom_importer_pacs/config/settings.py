from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


CONFIG_DIR = Path.home() / ".dicom-importer-pacs"
CONFIG_FILE = CONFIG_DIR / "settings.json"


@dataclass(slots=True)
class AeConfig:
    local_ae_title: str = "DICOMIMPORTER"
    local_port: int = 11112
    pacs_ae_title: str = "PACS"
    pacs_host: str = "127.0.0.1"
    pacs_port: int = 104


@dataclass(slots=True)
class AppSettings:
    ae: AeConfig
    max_name_len: int = 64
    max_accession_len: int = 32
    max_study_desc_len: int = 64

    @staticmethod
    def default() -> "AppSettings":
        return AppSettings(ae=AeConfig())


def load_settings() -> AppSettings:
    if not CONFIG_FILE.exists():
        return AppSettings.default()

    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return AppSettings.default()

    ae_raw = raw.get("ae", {})
    ae = AeConfig(
        local_ae_title=ae_raw.get("local_ae_title", "DICOMIMPORTER"),
        local_port=int(ae_raw.get("local_port", 11112)),
        pacs_ae_title=ae_raw.get("pacs_ae_title", "PACS"),
        pacs_host=ae_raw.get("pacs_host", "127.0.0.1"),
        pacs_port=int(ae_raw.get("pacs_port", 104)),
    )
    return AppSettings(
        ae=ae,
        max_name_len=int(raw.get("max_name_len", 64)),
        max_accession_len=int(raw.get("max_accession_len", 32)),
        max_study_desc_len=int(raw.get("max_study_desc_len", 64)),
    )


def save_settings(settings: AppSettings) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(asdict(settings), indent=2),
        encoding="utf-8",
    )
