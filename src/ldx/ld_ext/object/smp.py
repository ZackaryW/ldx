import json
import os

from ldx.ld_ext.base.cache import AttrMixin
from ..model.smp import SMP


class SMPFile(AttrMixin):

    def customizeList(self) -> list[str]:
        """List all .smp files in customizeConfigs directory."""
        return [
            os.path.basename(file)
            for file in os.listdir(self.attr.customizeConfigs)
            if os.path.isfile(os.path.join(self.attr.customizeConfigs, file))
            and file.endswith(".smp")
        ]

    def getCustomize(self, name: str) -> SMP:
        """Get a customized SMP file by name (with or without .smp extension)."""
        if not name.endswith(".smp"):
            name += ".smp"
        path = os.path.join(self.attr.customizeConfigs, name)
        return self._loadFile(path)

    def getRecommended(self, name: str) -> SMP:
        """Get a recommended SMP file by name (with or without .smp extension)."""
        if not name.endswith(".smp"):
            name += ".smp"
        path = os.path.join(self.attr.recommendedConfigs, name)
        return self._loadFile(path)

    def dump(self, path: str, smp: SMP):
        """Save an SMP file. Path can be absolute or relative to customizeConfigs."""
        # check file relative to appattr
        if not os.path.isabs(path):
            path = os.path.join(self.attr.customizeConfigs, path)

        with open(path, "w") as f:
            json.dump(smp, f, indent=4)

    @classmethod
    def load(cls, path: str) -> SMP:
        """Load an SMP file from an arbitrary path."""
        with open(path, "r") as f:
            return json.load(f)
