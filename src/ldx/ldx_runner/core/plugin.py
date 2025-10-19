
"""
Plugin system core components for ldx runner.

This module provides the plugin base class and metaclass for automatic
plugin registration. Plugins implement lifecycle hooks for automation workflows.
"""


class PluginMeta(type):
    """
    Metaclass for automatic plugin registration.
    
    All classes inheriting from LDXPlugin are automatically registered in the
    _type_registry dictionary, keyed by their __env_key__ attribute. This enables
    dynamic plugin discovery from configuration files.
    
    Attributes:
        _type_registry: Dict[str, Type[LDXPlugin]] - Maps env keys to plugin classes
    
    Example:
        ```python
        class MyPlugin(LDXPlugin):
            __env_key__ = "my_plugin"
            # Automatically registered as _type_registry["my_plugin"] = MyPlugin
        ```
    """
    _type_registry = {}

    def __new__(cls, name, bases, attrs):
        """
        Create new plugin class and register it.
        
        Args:
            name: Name of the class being created
            bases: Base classes
            attrs: Class attributes dictionary
        
        Returns:
            The newly created class, registered in _type_registry if not LDXPlugin base
        """
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "LDXPlugin":
            cls._type_registry[new_class.__env_key__] = new_class
        return new_class


class LDXPlugin(metaclass=PluginMeta):
    """
    Base class for all LDX runner plugins.
    
    Plugins implement lifecycle hooks to define automation behavior. Each plugin
    must define an __env_key__ that matches the section name in TOML config files.
    
    Lifecycle Flow:
        1. onEnvLoad(env) - Parse configuration from TOML section
        2. canRun(cfg, instance) - Pre-execution validation
        3. onStartup(cfg, instance) - Initialize and start operations
        4. shouldStop(cfg, instance) - Runtime termination check (polled)
        5. onShutdown(cfg, instance) - Cleanup and teardown
    
    Attributes:
        __env_key__: Configuration key that maps to this plugin (must be set by subclasses)
    
    Example Plugin:
        ```python
        from dataclasses import dataclass
        
        @dataclass
        class MyPluginModel:
            param: str
        
        class MyPlugin(LDXPlugin):
            __env_key__ = "my_plugin"
            
            def onEnvLoad(self, env):
                self.model = MyPluginModel(**env)
            
            def onStartup(self, cfg, instance):
                print(f"Starting with {self.model.param}")
        ```
    
    Example Configuration:
        ```toml
        [my_plugin]
        param = "value"
        ```
    """
    __env_key__ :  str = None


    def onEnvLoad(self, env : dict):
        """
        Load and parse plugin configuration from TOML section.
        
        Called first in the lifecycle. This is where plugins should parse their
        configuration into internal models/dataclasses and perform validation.
        
        Args:
            env: Dictionary containing the plugin's configuration section from TOML
        
        Raises:
            ValueError: If configuration validation fails
        
        Example:
            ```python
            def onEnvLoad(self, env):
                self.model = MyConfigModel(**env)
                if not self.model.required_field:
                    raise ValueError("required_field must be set")
            ```
        """
        pass

    def onStartup(self, cfg : dict, instance):
        """
        Initialize and start plugin operations.
        
        Called after all plugins have loaded and passed canRun() checks.
        This is where plugins perform their main startup actions like launching
        applications, connecting to services, etc.
        
        Args:
            cfg: Complete configuration dictionary (all plugin sections)
            instance: LDXInstance runner instance providing access to other plugins
        
        Example:
            ```python
            def onStartup(self, cfg, instance):
                self.process = subprocess.Popen([self.model.executable])
                print(f"Started process {self.process.pid}")
            ```
        """
        pass

    def canRun(self, cfg : dict, instance) -> bool:
        """
        Pre-execution validation check.
        
        Called before onStartup(). If any plugin returns False, the entire
        execution is aborted (all-or-nothing model). Use this to verify
        prerequisites, check file existence, validate configuration, etc.
        
        Args:
            cfg: Complete configuration dictionary (all plugin sections)
            instance: LDXInstance runner instance
        
        Returns:
            True if plugin can run successfully, False to abort execution
        
        Example:
            ```python
            def canRun(self, cfg, instance):
                if not os.path.exists(self.model.data_file):
                    print(f"Data file not found: {self.model.data_file}")
                    return False
                return True
            ```
        """
        return True
    
    def shouldStop(self, cfg : dict, instance) -> bool:
        """
        Runtime termination condition check.
        
        Called repeatedly in the main execution loop (every ~1 second).
        If any plugin returns True, the execution stops and all plugins
        proceed to onShutdown(). Use this to implement time limits,
        completion detection, error conditions, etc.
        
        Args:
            cfg: Complete configuration dictionary (all plugin sections)
            instance: LDXInstance runner instance
        
        Returns:
            True to stop execution, False to continue running
        
        Example:
            ```python
            def shouldStop(self, cfg, instance):
                if datetime.now() >= self.target_time:
                    print("Time limit reached")
                    return True
                return False
            ```
        """
        return False
    
    def onShutdown(self, cfg : dict, instance):
        """
        Cleanup and teardown operations.
        
        Called after execution stops (either from shouldStop() or interruption).
        Always called, even if errors occur. Use this to close connections,
        terminate processes, save state, etc.
        
        Args:
            cfg: Complete configuration dictionary (all plugin sections)
            instance: LDXInstance runner instance
        
        Example:
            ```python
            def onShutdown(self, cfg, instance):
                if hasattr(self, 'process'):
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    print("Process terminated")
            ```
        """
        pass
    
    def getSchedule(self) -> dict | None:
        """
        Return APScheduler-compatible schedule configuration.
        
        This method is used by the Flask server to extract scheduling metadata.
        Return None if this plugin doesn't define scheduling, or return a dict
        with APScheduler job parameters.
        
        Returns:
            Dictionary with APScheduler parameters, or None if no schedule
        
        Example:
            ```python
            def getSchedule(self):
                return {
                    'trigger': 'cron',
                    'hour': '*/2',  # Every 2 hours
                    'minute': '0'
                }
            ```
        
        Note:
            Schedule is metadata about *when* to run, not *what* to run.
            This is typically implemented by dedicated schedule plugins,
            not by business logic plugins.
        """
        return None

    

    