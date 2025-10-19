import json
import os
from dataclasses import asdict

from ldx.ld_ext.base.cache import AttrMixin
from ..model.record import Record, RecordInfo, Operation


class RecordFile(AttrMixin):

    def recordList(self) -> list[str]:
        """List all .record files in operationRecords directory."""
        return [
            os.path.basename(file)
            for file in os.listdir(self.attr.operationRecords)
            if os.path.isfile(os.path.join(self.attr.operationRecords, file))
            and file.endswith(".record")
        ]

    def getRecord(self, name: str) -> Record:
        """Get a record file by name (with or without .record extension)."""
        if not name.endswith(".record"):
            name += ".record"
        path = os.path.join(self.attr.operationRecords, name)
        raw = self._loadFile(path)
        return Record(
            recordInfo=RecordInfo(**raw["recordInfo"]),
            operations=[Operation(**operation) for operation in raw["operations"]],
        )

    def dump(self, path: str, record: Record):
        """Save a record file. Path can be absolute or relative to operationRecords."""
        # check file relative to appattr
        if not os.path.isabs(path):
            path = os.path.join(self.attr.operationRecords, path)

        with open(path, "w") as f:
            json.dump(asdict(record), f, indent=4)

    @classmethod
    def load(cls, path: str) -> Record:
        """Load a record file from an arbitrary path."""
        with open(path, "r") as f:
            data = json.load(f)
            return Record(
                recordInfo=RecordInfo(**data["recordInfo"]),
                operations=[Operation(**operation) for operation in data["operations"]],
            )
