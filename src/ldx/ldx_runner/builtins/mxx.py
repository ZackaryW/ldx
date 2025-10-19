

from dataclasses import dataclass
import os
from ldx.ldx_runner.core.plugin import LDXPlugin
from ldx.utils.subprocess import open_detached

@dataclass
class MXXModel:
    scoop : bool = True
    pkg : str = None

    path : str = None

    targetExe : str = None

    delay : int = 10

    def __post_init__(self):
        if not self.targetExe:
            raise ValueError("targetExe must be specified for MXX configuration.")

        if self.scoop and not self.pkg:
            raise ValueError("pkg must be specified when scoop is True for MXX configuration.")
        
        if self.scoop and self.path:
            raise ValueError("path should not be specified when scoop is True for MXX configuration.")
        

class MXX(LDXPlugin):
    __env_key__ : str = "mxx"

    def onEnvLoad(self, env):
        self.model = MXXModel(**env)

    def onStartup(self, cfg, instance):
        if self.model.scoop:
            scoop_path = os.environ.get("SCOOP", os.path.expanduser("~\\scoop"))
            mxx_path = os.path.join(scoop_path, "apps", self.model.pkg, "current", self.model.targetExe)

            if not os.path.isfile(mxx_path):
                raise FileNotFoundError(f"MXX executable not found at {mxx_path}")
            
            self.executable_path = mxx_path

        else:
            mxx_path = os.path.join(self.model.path, self.model.targetExe)
            if not os.path.isfile(mxx_path):
                raise FileNotFoundError(f"MXX executable not found at {mxx_path}")
            
            self.executable_path = mxx_path

        open_detached([self.executable_path])


    def onShutdown(self, cfg, instance):
        os.system(f"taskkill /IM {self.model.targetExe} /F")

