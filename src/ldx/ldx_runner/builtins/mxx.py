

"""
MXX (Macro/Script Executor) plugin for launching external executables.

This plugin manages external executable applications, supporting both
Scoop-managed installations and custom paths.
"""

from dataclasses import dataclass
import os
from ldx.ldx_runner.core.plugin import LDXPlugin
from ldx.utils.subprocess import open_detached

@dataclass
class MXXModel:
    """
    Configuration model for MXX executable launcher.
    
    Attributes:
        scoop: Whether to use Scoop package manager path resolution (default: True)
        pkg: Scoop package name (required if scoop=True)
        path: Custom path to executable directory (required if scoop=False)
        targetExe: Name of the executable file to launch (required)
        delay: Delay in seconds before launching (default: 10)
    
    Raises:
        ValueError: If configuration validation fails
    
    Examples:
        Scoop-managed executable:
        ```toml
        [mxx]
        scoop = true
        pkg = "my-tool"
        targetExe = "tool.exe"
        ```
        
        Custom path executable:
        ```toml
        [mxx]
        scoop = false
        path = "C:/Tools/MyApp"
        targetExe = "app.exe"
        ```
    """
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
    """
    External executable launcher plugin.
    
    Launches and manages external executables with support for:
    - Scoop package manager integration (automatic path resolution)
    - Custom executable paths
    - Automatic termination on shutdown
    
    Config Key: "mxx"
    
    The plugin resolves the executable path based on configuration,
    verifies the file exists, launches it in detached mode, and
    terminates it on shutdown.
    
    Example Configurations:
        Scoop-managed:
        ```toml
        [mxx]
        scoop = true
        pkg = "my-app"
        targetExe = "app.exe"
        ```
        
        Custom path:
        ```toml
        [mxx]
        scoop = false
        path = "C:/MyApps/Tool"
        targetExe = "tool.exe"
        delay = 5
        ```
    """
    __env_key__ : str = "mxx"

    def onEnvLoad(self, env):
        """
        Load and validate configuration.
        
        Args:
            env: Dictionary containing MXX configuration
        
        Raises:
            ValueError: If configuration validation fails
        """
        self.model = MXXModel(**env)

    def onStartup(self, cfg, instance):
        """
        Resolve executable path and launch the application.
        
        For Scoop installations, resolves path using SCOOP environment variable
        or default location. For custom paths, uses the provided directory.
        Verifies the executable exists before launching.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        
        Raises:
            FileNotFoundError: If the executable file does not exist
        """
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
        """
        Forcefully terminate the launched executable.
        
        Uses Windows taskkill command to terminate the process by executable name.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        """
        os.system(f"taskkill /IM {self.model.targetExe} /F")

