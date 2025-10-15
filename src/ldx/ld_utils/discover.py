import psutil
from pathlib import Path

def discover_process():
    """
    Discover the LDPlayer installation directory by searching running processes.
    
    This function searches through running processes to find LDPlayer-related processes
    (dnplayer.exe or processes with "dn" in their name) and traverses the directory
    structure to locate the LDPlayer installation directory.
    
    Returns:
        Path: The absolute path to the LDPlayer installation directory,
              or None if LDPlayer is not found running.
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == "dnplayer.exe":
                return Path(proc.exe()).parent.resolve()
            if "dn" in proc.name():
                path = Path(proc.exe()).parent.resolve()
                counter = 0
                while True:
                    contents = [item.name for item in path.iterdir()]
                    if "dnplayer.exe" in contents:
                        return path
                    elif "LDPlayer" in contents:
                        path = path / "LDPlayer"
                    else:
                        path = path.parent
                    counter += 1
                    if counter > 5:
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

