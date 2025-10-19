"""
OS command execution plugin for running arbitrary system commands.

This plugin executes system commands at startup and optionally registers
processes for cleanup via the lifetime plugin.
"""

from dataclasses import dataclass
import datetime
import os
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class OSModel:
    """
    Configuration model for OS command execution.
    
    Attributes:
        cmd: System command to execute at startup
        kill: Optional process name to terminate on shutdown (requires lifetime plugin)
    
    Example:
        ```toml
        [os]
        cmd = "start notepad.exe"
        kill = "notepad.exe"
        ```
    """
    cmd : str
    kill : str = None

class LDXOS(LDXPlugin):
    """
    System command execution plugin.
    
    Executes arbitrary OS commands at startup and optionally registers
    processes for cleanup when the lifetime plugin is present.
    
    Config Key: "os"
    
    Features:
        - Execute any system command via os.system()
        - Register processes for automatic cleanup on shutdown
        - Integrates with lifetime plugin for process management
    
    Example Configuration:
        ```toml
        [os]
        cmd = "start C:/Tools/monitor.exe"
        kill = "monitor.exe"
        
        [lifetime]
        lifetime = 3600
        ```
    
    Notes:
        - Commands are executed synchronously
        - If 'kill' is specified and lifetime plugin is loaded, the process
          will be added to the lifetime plugin's kill list
        - Supports both simple process names and commands with arguments
    """
    __env_key__ : str = "os"

    def onEnvLoad(self, env):
        """
        Load configuration from environment.
        
        Args:
            env: Dictionary containing OS command configuration
        """
        self.model = OSModel(**env)

    def onStartup(self, cfg, instance):
        """
        Execute the configured system command.
        
        If a kill target is specified and the lifetime plugin is loaded,
        registers the process for automatic termination on shutdown.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance containing loaded plugins
        """
        os.system(self.model.cmd)
        if self.model.kill and "lifetime" in instance.plugins:
            if " " in self.model.kill:
                instance.plugins.get("lifetime").killList.append(("cmd", self.model.kill.split(" ")[0]))
            else:
                instance.plugins.get("lifetime").killList.append(("process", self.model.kill))

        