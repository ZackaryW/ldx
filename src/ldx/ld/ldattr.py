from dataclasses import dataclass
from functools import cached_property
import os
import subprocess
import typing

@dataclass
class LDAttr:
    path : str
    validate : bool = True
    interval_between_batches : float = 5.0
    
    def __post_init__(self):
        self.path = os.path.abspath(self.path)
        if self.validate and not self.isValid:
            raise ValueError(f"Invalid LDPlayer path: {self.path}")


    @classmethod
    def from_user(cls, index : int = 0) -> 'LDAttr':
        """
        creates a Console instance from the user config
        """
        from ldx.ld_utils.config import LD_CONFIG
        from ldx.ld.ldattr import LDAttr

        if not LD_CONFIG["path"] or index >= len(LD_CONFIG["path"]):
            raise ValueError("LDPlayer installation directory not found.")
        else:
            path = LD_CONFIG["path"][index]

        return LDAttr(path)

    @classmethod
    def discover(cls, fallback_user_config: bool = True) -> typing.Optional['LDAttr']:
        from ldx.ld_utils.discover import discover_process
        path = discover_process()
        if not path:
            # If no path is found, fall back to user config
            if fallback_user_config:
                return cls.from_user()
            return None
        return LDAttr(path)

    def __eq__(self, other: "LDAttr"):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)

    @cached_property
    def dnconsole(self) -> str:
        return os.path.join(self.path, "dnconsole.exe")

    @cached_property
    def ldconsole(self) -> str:
        return os.path.join(self.path, "ldconsole")

    @cached_property
    def vmfolder(self) -> str:
        return os.path.join(self.path, "vms")

    @cached_property
    def customizeConfigs(self) -> str:
        return os.path.join(self.vmfolder, "customizeConfigs")

    @cached_property
    def recommendedConfigs(self) -> str:
        return os.path.join(self.vmfolder, "recommendConfigs")

    @cached_property
    def operationRecords(self) -> str:
        return os.path.join(self.vmfolder, "operationRecords")

    @cached_property
    def config(self) -> str:
        return os.path.join(self.vmfolder, "config")

    @property
    def isValid(self) -> bool:
        s = subprocess.run(self.ldconsole, capture_output=True, text=True)
        code = s.returncode

        return all(
            [
                os.path.exists(self.dnconsole),
                os.path.exists(self.vmfolder),
                os.path.exists(self.customizeConfigs),
                os.path.exists(self.recommendedConfigs),
                os.path.exists(self.operationRecords),
                os.path.exists(self.config),
                code == 0,
            ]
        )
