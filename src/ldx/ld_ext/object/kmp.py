import json

from ldx.ld_ext.base.cache import AttrMixin
from ..model.kmp import KeyboardMapping
import os
class KMPFile(AttrMixin):

    def customizeList(self) -> list[str]:
        """List all .kmp files in customizeConfigs directory."""
        return [
            os.path.basename(file)
            for file in os.listdir(self.attr.customizeConfigs)
            if os.path.isfile(os.path.join(self.attr.customizeConfigs, file))
            and file.endswith(".kmp")
        ]

    def getCustomize(self, name: str) -> KeyboardMapping:
        """Get a customized KMP file by name (with or without .kmp extension)."""
        if not name.endswith(".kmp"):
            name += ".kmp"
        path = os.path.join(self.attr.customizeConfigs, name)
        raw = self._loadFile(path)
        return KeyboardMapping.from_dict(raw)

    def getRecommended(self, name: str) -> KeyboardMapping:
        """Get a recommended KMP file by name (with or without .kmp extension)."""
        if not name.endswith(".kmp"):
            name += ".kmp"
        path = os.path.join(self.attr.recommendedConfigs, name)
        raw = self._loadFile(path)
        return KeyboardMapping.from_dict(raw)

    @classmethod
    def load(cls, path: str) -> KeyboardMapping:
        """Load a KMP file from an arbitrary path."""
        with open(path, "r") as f:
            raw = json.load(f)
        return KeyboardMapping.from_dict(raw)

    def dump(self, path: str, mapping: KeyboardMapping):
        """Save a KMP file. Path can be absolute or relative to customizeConfigs."""
        # check file relative to appattr
        if not os.path.isabs(path):
            path = os.path.join(self.attr.customizeConfigs, path)

        with open(path, "w") as f:
            json.dump(mapping.to_dict(), f, indent=4)