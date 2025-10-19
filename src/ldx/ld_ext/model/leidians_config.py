from dataclasses import asdict, dataclass
from typing import TypedDict
import typing
from ldx.ld_utils.dict import flatten_nested_dict, parse_dotted_dict


class WindowsPosition(TypedDict):
    x: int
    y: int


class BasicSettings(TypedDict):
    lastIp: typing.Optional[str]


@dataclass
class LeidiansConfig:
    nextCheckupdateTime: int = 0
    hasPluginLast: bool = False
    strp: str = ""
    lastZoneArea: str = ""
    lastZoneName: str = ""
    vipMode: bool = False
    isBaseboard: bool = False
    basicSettings: BasicSettings = None
    noiceUserRed: bool = False
    isFirstInstallApk: bool = False
    cloneFromSmallDisk: bool = False
    languageId: str = ""
    mulTab: bool = False
    exitFullscreenEsc: bool = False
    disableMouseRightOpt: bool = False
    nextUpdateTime: int = 0
    ignoreVersion: str = ""
    framesPerSecond: int = 60
    reduceAudio: bool = False
    displayMode: bool = False
    vmdkFastMode: bool = False
    windowsAlignType: int = 0
    windowsRowCount: int = 0
    windowsAutoSize: bool = False
    sortwndnotoutscreen: bool = False
    moreScreenSortInSame: bool = False
    windowsOrigin: WindowsPosition = None
    windowsOffset: WindowsPosition = None
    batchStartInterval: int = 5
    batchNewCount: int = 0
    batchCloneCount: int = 0
    windowsRecordPos: bool = False
    multiPlayerSort: int = 0
    isSSD: bool = False
    fromInstall: bool = False
    productLanguageId: str = ""
    channelOpenId: str = ""
    channelLastOpenId: str = ""
    operaRecordFirstDo: bool = False
    remoteEntranceVersion: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        data = parse_dotted_dict(data)
        data = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}

        return cls(**data)

    def to_dict(self) -> dict:
        data = asdict(self)
        data = flatten_nested_dict(data)
        return data