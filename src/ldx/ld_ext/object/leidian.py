import json
import os
import typing

from ldx.ld_ext.base.cache import AttrMixin
from ..model.leidian_config import LeidianConfig
from ..model.leidians_config import LeidiansConfig


class LeidianFile(AttrMixin):

    def listLeidianConfigs(self) -> list[str]:
        """List all leidian config files (excluding leidians.config)."""
        return [
            os.path.join(self.attr.config, file)
            for file in os.listdir(self.attr.config)
            if file.endswith(".config")
            and file.startswith("leidian")
            and file != "leidians.config"
        ]

    def getLeidiansConfig(self) -> LeidiansConfig:
        """Get the main leidians.config file."""
        path = os.path.join(self.attr.config, "leidians.config")
        raw = self._loadFile(path)
        return LeidiansConfig.from_dict(raw)

    def getLeidianConfig(self, id_or_name: typing.Union[int, str]) -> LeidianConfig:
        """Get a specific leidian config by ID or name."""
        # Handle string that is actually a digit
        if isinstance(id_or_name, str) and id_or_name.isdigit():
            id_or_name = int(id_or_name)
        
        # Handle string starting with "leidian" (e.g., "leidian123")
        if isinstance(id_or_name, str) and id_or_name.startswith("leidian"):
            instance_id = id_or_name[7:]  # Remove "leidian" prefix
            path = os.path.join(self.attr.config, f"{id_or_name}.config")
        else:
            # Assume it's an ID
            instance_id = id_or_name
            path = os.path.join(self.attr.config, f"leidian{instance_id}.config")
        
        raw = self._loadFile(path)
        return LeidianConfig.from_dict(raw)

    def getMultipleLeidianConfigs(self, ids: list[int]) -> dict[int, LeidianConfig]:
        """Get multiple leidian configs by their IDs."""
        return {
            meta: LeidianConfig.from_dict(
                self._loadFile(
                    os.path.join(self.attr.config, f"leidian{meta}.config")
                )
            )
            for meta in ids
        }

    def dumpLeidiansConfig(self, config: LeidiansConfig):
        """Save the main leidians.config file."""
        path = os.path.join(self.attr.config, "leidians.config")
        with open(path, "w") as f:
            json.dump(config.to_dict(), f, indent=4)

    def dumpLeidianConfig(self, config: LeidianConfig):
        """Save a specific leidian config file."""
        path = os.path.join(self.attr.config, f"leidian{config.id}.config")
        with open(path, "w") as f:
            json.dump(config.to_dict(), f, indent=4)

    @classmethod
    def loadLeidiansConfig(cls, path: str) -> LeidiansConfig:
        """Load leidians config from an arbitrary path."""
        with open(path, "r") as f:
            return LeidiansConfig.from_dict(json.load(f))

    @classmethod
    def loadLeidianConfig(cls, path: str) -> LeidianConfig:
        """Load leidian config from an arbitrary path."""
        with open(path, "r") as f:
            return LeidianConfig.from_dict(json.load(f))
