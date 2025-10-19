

"""
LDPlayer control plugin for launching and managing emulator instances.

This plugin provides lifecycle management for LDPlayer emulator instances,
including launching with or without specific apps and automatic cleanup on shutdown.
"""

from dataclasses import dataclass
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class LDModel:
    """
    Configuration model for LDPlayer instance control.
    
    Attributes:
        name: Name of the emulator instance (mutually exclusive with index)
        index: Index of the emulator instance (mutually exclusive with name)
        path: Optional custom path to ldconsole.exe (auto-discovered if not provided)
        pkg: Optional package name to launch immediately after starting emulator
        close: Whether to automatically close the emulator on shutdown (default: True)
    
    Raises:
        ValueError: If neither name nor index is provided, or if both are provided
    
    Example:
        ```toml
        [ld]
        name = "MyEmulator"
        pkg = "com.example.app"
        close = true
        ```
    """
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
    """
    LDPlayer instance management plugin.
    
    This plugin controls LDPlayer emulator instances throughout their lifecycle:
    - Discovers or uses specified LDPlayer installation
    - Launches emulator by name or index
    - Optionally launches a specific app package on startup
    - Automatically closes emulator on shutdown if configured
    
    Config Key: "ld"
    
    Example Configuration:
        ```toml
        [ld]
        name = "MyEmulator"
        pkg = "com.example.game"
        close = true
        ```
    """
    
    def onEnvLoad(self, env):
        """
        Load and validate configuration from environment.
        
        Args:
            env: Dictionary containing LD configuration parameters
        
        Raises:
            ValueError: If configuration validation fails
        """
        self.model = LDModel(**env)

    def onStartup(self, cfg, instance):
        """
        Launch the LDPlayer emulator instance.
        
        Discovers LDPlayer installation (or uses configured path), creates console
        connection, and launches the emulator. If a package is specified, launches
        the app directly using launchex.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        """
        ldattr = LDAttr(self.model.path) if self.model.path else LDAttr.discover()

        console = Console(ldattr)
        
        if self.model.pkg:
            console.launchex(self.model.name, self.model.index, self.model.pkg)

        else:
            console.launch(self.model.name, self.model.index)

    def onShutdown(self, cfg, instance):
        """
        Close the emulator instance if configured to do so.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        """
        if self.model.close:
            console = Console(LDAttr.discover())
            console.quit(self.model.name, self.model.index)


