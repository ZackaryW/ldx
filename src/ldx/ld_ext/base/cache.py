
import json
import os
import typing

from ldx.ld.ldattr import LDAttr

class FileMeta(typing.TypedDict):
    mtime : int
    ac : int # access count


class AttrMeta(type):
    _opened_files : typing.Dict[str, dict | list] = {}
    _opened_meta : typing.Dict[str, FileMeta] = {}

    _kv : typing.Dict[str, dict | list] = {}
    _kv_meta : typing.Dict[str, FileMeta] = {}

    _total_cached : int = 1000

class AttrMixin(metaclass=AttrMeta):
    def __init__(self, path : typing.Union[str, LDAttr]):
        if isinstance(path, str):
            self.attr = LDAttr(path)
        else:
            self.attr = path

    def __real_load__(self, path : str):
        
        # eviction - need to make room for the new file
        if len(AttrMeta._opened_files) >= AttrMeta._total_cached:
            # evict least accessed (LFU - Least Frequently Used)
            sorted_meta = sorted(
                AttrMeta._opened_meta.items(),
                key=lambda item: item[1]["ac"]
            )
            # +1 to make room for the new file we're about to add
            num_to_evict = len(AttrMeta._opened_files) - AttrMeta._total_cached + 1
            to_evict = sorted_meta[:num_to_evict]
            for evict_path, _ in to_evict:
                del AttrMeta._opened_files[evict_path]
                del AttrMeta._opened_meta[evict_path]

        # actual load

        with open(path, "r") as f:
            raw = f.read()
        data = json.loads(raw)
        AttrMeta._opened_files[path] = data
        AttrMeta._opened_meta[path] = FileMeta(
            mtime = os.path.getmtime(path),
            ac = 1
        )

        return data
    

    def _loadFile(self, path : str):
        # if file no longer exists
        if not os.path.exists(path):
            if path in AttrMeta._opened_files:
                del AttrMeta._opened_files[path]
            if path in AttrMeta._opened_meta:
                del AttrMeta._opened_meta[path]
            return None

        if path in AttrMeta._opened_files and AttrMeta._opened_meta.get(path, {}).get("mtime", 0) == os.path.getmtime(path):
            AttrMeta._opened_meta[path]["ac"] += 1
            return AttrMeta._opened_files[path]

        raw = self.__real_load__(path)
        return raw

    