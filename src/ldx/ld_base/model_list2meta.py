import typing


class List2Meta(typing.TypedDict):
    id: int
    name: str
    top_window_handle: int
    bind_window_handle: int
    android_started_int: int
    pid: int
    pid_of_vbox: int


def list2alias(data: List2Meta) -> dict:
    return {
        "id": data["id"],
        "name": data["name"],
        "top_window_handle": data["top_window_handle"],
        "twh": data["top_window_handle"],
        "topWindowHandle": data["top_window_handle"],
        "bind_window_handle": data["bind_window_handle"],
        "bwh": data["bind_window_handle"],
        "bindWindowHandle": data["bind_window_handle"],
        "android_started_int": data["android_started_int"],
        "isStarted": data["android_started_int"],
        "pid": data["pid"],
        "pid_of_vbox": data["pid_of_vbox"],
        "vboxPid": data["pid_of_vbox"],
        "pidOfVbox": data["pid_of_vbox"],
    }