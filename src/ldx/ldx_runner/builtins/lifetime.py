

from dataclasses import dataclass
import datetime
import logging
import os
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class LifetimeModel:
    lifetime : int

class LDXLifetime(LDXPlugin):
    __env_key__ : str = "lifetime"

    def onEnvLoad(self, env):
        self.model = LifetimeModel(**env)
        self.killList = []

    def canRun(self, cfg, instance):
        if self.model.lifetime <= 0:
            return False

        return super().canRun(cfg, instance)

    def onStartup(self, cfg, instance):
        self.targetStopTime = datetime.datetime.now() + datetime.timedelta(seconds=self.model.lifetime)

    def shouldStop(self, cfg, instance):
        if datetime.datetime.now() >= self.targetStopTime:
            return True

        return super().shouldStop(cfg, instance)
    
    def onShutdown(self, cfg, instance):
        for killItem in self.killList:
            match killItem:
                case ("process", procName):
                    logging.info(f"Terminating process: {procName}")
                    import psutil
                    for proc in psutil.process_iter():
                        if proc.name() == procName:
                            proc.terminate()
                            proc.wait(timeout=5)
                case ("cmd", cmdName):
                    logging.info(f"Terminating command: {cmdName}")
                    os.system(f"taskkill /IM {cmdName} /F")
                case ("taskkill", taskName):
                    logging.info(f"Terminating task: {taskName}")
                    os.system(f"taskkill /IM {taskName} /F")
                case _:
                    pass

        self.killList.clear()