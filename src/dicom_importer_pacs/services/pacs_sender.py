from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import (
    ComputedRadiographyImageStorage,
    CTImageStorage,
    DigitalXRayImageStorageForPresentation,
    MRImageStorage,
    SecondaryCaptureImageStorage,
)


# Common transfer syntaxes including lossless JPEG and JPEG2000.
TRANSFER_SYNTAXES = [
    "1.2.840.10008.1.2",  # Implicit VR Little Endian
    "1.2.840.10008.1.2.1",  # Explicit VR Little Endian
    "1.2.840.10008.1.2.4.57",  # JPEG Lossless
    "1.2.840.10008.1.2.4.70",  # JPEG Lossless SV1
    "1.2.840.10008.1.2.4.90",  # JPEG 2000 Lossless
    "1.2.840.10008.1.2.4.91",  # JPEG 2000
]


@dataclass(slots=True)
class PacsConnection:
    local_ae_title: str
    remote_ae_title: str
    remote_host: str
    remote_port: int


class PacsSenderError(Exception):
    """Raised when C-STORE transmission fails."""


class PacsSender:
    def __init__(self, connection: PacsConnection) -> None:
        self.connection = connection

    def _build_ae(self) -> AE:
        ae = AE(ae_title=self.connection.local_ae_title)
        for context in (
            CTImageStorage,
            MRImageStorage,
            ComputedRadiographyImageStorage,
            DigitalXRayImageStorageForPresentation,
            SecondaryCaptureImageStorage,
        ):
            ae.add_requested_context(context, TRANSFER_SYNTAXES)
        return ae

    def send(
        self,
        datasets: list[Dataset],
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> None:
        ae = self._build_ae()
        assoc = ae.associate(
            self.connection.remote_host,
            self.connection.remote_port,
            ae_title=self.connection.remote_ae_title,
        )
        if not assoc.is_established:
            raise PacsSenderError("Unable to establish association with PACS")

        try:
            total = len(datasets)
            for idx, ds in enumerate(datasets, start=1):
                status = assoc.send_c_store(ds)
                code = getattr(status, "Status", None)
                if code not in (0x0000,):
                    raise PacsSenderError(
                        f"C-STORE failed for SOPInstanceUID={getattr(ds, 'SOPInstanceUID', 'UNKNOWN')} status={code}"
                    )
                if progress_callback:
                    progress_callback(idx, total, "Sent via C-STORE")
        finally:
            assoc.release()
