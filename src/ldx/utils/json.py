import json
import pathlib

def touch_json(path, default_data = {}):
    path = pathlib.Path(path)

    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_json(path, data):
    path = pathlib.Path(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)    