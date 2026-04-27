from __future__ import annotations

import ctypes
from pathlib import Path


DRIVE_CDROM = 5


def list_cdrom_roots() -> list[Path]:
    roots: list[Path] = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
        if drive_type == DRIVE_CDROM:
            roots.append(Path(drive))
    return roots
