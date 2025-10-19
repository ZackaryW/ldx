from dataclasses import dataclass
import datetime
import os
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class OSModel:
    cmd : str
    kill : str = None

class LDXOS(LDXPlugin):
    __env_key__ : str = "os"

    def onEnvLoad(self, env):
        self.model = OSModel(**env)

    def onStartup(self, cfg, instance):
        os.system(self.model.cmd)
        if self.model.kill and "lifetime" in instance.plugins:
            if " " in self.model.kill:
                instance.plugins.get("lifetime").killList.append(("cmd", self.model.kill.split(" ")[0]))
            else:
                instance.plugins.get("lifetime").killList.append(("process", self.model.kill))

        