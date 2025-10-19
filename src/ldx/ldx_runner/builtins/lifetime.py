

"""
Lifetime control plugin for time-based execution limits.

This plugin manages the duration of runner execution and provides cleanup
capabilities for processes, commands, and tasks at shutdown.
"""

from dataclasses import dataclass
import datetime
import logging
import os
from ldx.ldx_runner.core.plugin import LDXPlugin

@dataclass
class LifetimeModel:
    """
    Configuration model for lifetime control.
    
    Attributes:
        lifetime: Duration in seconds for which the runner should execute
    
    Example:
        ```toml
        [lifetime]
        lifetime = 3600  # Run for 1 hour
        ```
    """
    lifetime : int

class LDXLifetime(LDXPlugin):
    """
    Time-based execution control plugin.
    
    Controls how long the runner executes and provides process cleanup at shutdown.
    Other plugins can register items to kill on shutdown by adding to the killList.
    
    Config Key: "lifetime"
    
    Features:
        - Sets execution duration in seconds
        - Stops runner when time expires
        - Kills registered processes/commands on shutdown
        - Integrates with other plugins for cleanup coordination
    
    Example Configuration:
        ```toml
        [lifetime]
        lifetime = 3600  # Run for 1 hour
        ```
    
    Kill List Format:
        Plugins can add items to self.killList as tuples:
        - ("process", "process_name.exe") - Terminate by process name using psutil
        - ("cmd", "command") - Terminate using taskkill /IM
        - ("taskkill", "task_name") - Terminate using taskkill /IM
    """
    __env_key__ : str = "lifetime"

    def onEnvLoad(self, env):
        """
        Load configuration and initialize kill list.
        
        Args:
            env: Dictionary containing lifetime configuration
        """
        self.model = LifetimeModel(**env)
        self.killList = []

    def canRun(self, cfg, instance):
        """
        Check if lifetime is valid (greater than 0).
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        
        Returns:
            False if lifetime <= 0, otherwise defers to parent
        """
        if self.model.lifetime <= 0:
            return False

        return super().canRun(cfg, instance)

    def onStartup(self, cfg, instance):
        """
        Calculate and store the target stop time.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        """
        self.targetStopTime = datetime.datetime.now() + datetime.timedelta(seconds=self.model.lifetime)

    def shouldStop(self, cfg, instance):
        """
        Check if the target stop time has been reached.
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        
        Returns:
            True if current time >= target stop time, otherwise defers to parent
        """
        if datetime.datetime.now() >= self.targetStopTime:
            return True

        return super().shouldStop(cfg, instance)
    
    def onShutdown(self, cfg, instance):
        """
        Terminate all registered processes, commands, and tasks.
        
        Iterates through killList and terminates items based on their type:
        - process: Uses psutil to find and terminate by name
        - cmd/taskkill: Uses Windows taskkill command
        
        Args:
            cfg: Full configuration dictionary
            instance: LDXInstance runner instance
        """
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