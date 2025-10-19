

from dataclasses import dataclass
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class LDModel:
    name : str = None
    index : int = None
    path : str = None
    pkg : str = None
    close : bool = True
    
    def __post_init__(self):
        if not self.name and not self.index:
            raise ValueError("Either name or index must be provided for LD configuration.")

        if self.name and self.index:
            raise ValueError("Only one of name or index should be provided for LD configuration.")


class LD(LDXPlugin):
    def onEnvLoad(self, env):
        self.model = LDModel(**env)

    def onStartup(self, cfg, instance):
        ldattr = LDAttr(self.model.path) if self.model.path else LDAttr.discover()

        console = Console(ldattr)
        
        if self.model.pkg:
            console.launchex(self.model.name, self.model.index, self.model.pkg)

        else:
            console.launch(self.model.name, self.model.index)

    def onShutdown(self, cfg, instance):
        if self.model.close:
            console = Console(LDAttr.discover())
            console.quit(self.model.name, self.model.index)


