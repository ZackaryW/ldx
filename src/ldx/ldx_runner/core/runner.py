"""
Runner implementations for LDX plugin execution.

This module provides two runner classes:
- LDXInstance: Direct plugin execution from config dictionary
- LDXRunner: Configuration manager with templates and global settings
"""

from pathlib import Path
import time
from .plugin import LDXPlugin, PluginMeta
import toml

class LDXInstance:
    """
    Simple synchronous runner for CLI usage.
    
    Executes plugins immediately without scheduling. Takes a configuration
    dictionary, loads matching plugins, and executes their lifecycle.
    
    Attributes:
        config: Configuration dictionary (typically from TOML file)
        plugins: Dict[str, LDXPlugin] - Loaded plugin instances keyed by env_key
    
    Lifecycle:
        1. load_plugins() - Instantiate and configure plugins from config
        2. Check all canRun() - Abort if any plugin fails (all-or-nothing)
        3. Call all onStartup() - Initialize all plugins
        4. Loop checking shouldStop() - Run until any plugin signals stop
        5. Call all onShutdown() - Cleanup (always, even on error)
    
    Example:
        ```python
        import toml
        from ldx.ldx_runner.core.runner import LDXInstance
        
        config = toml.load("automation.toml")
        runner = LDXInstance(config)
        runner.run()
        ```
    
    Example Configuration:
        ```toml
        [ld]
        name = "MyEmulator"
        pkg = "com.example.app"
        
        [lifetime]
        lifetime = 3600
        ```
    """
    
    def __init__(self, config: dict):
        """
        Initialize runner with configuration.
        
        Args:
            config: Configuration dictionary with plugin sections
        """
        self.config = config
        self.plugins : dict[str, LDXPlugin] = {}
    
    def load_plugins(self):
        """
        Load and instantiate plugins from configuration.
        
        Iterates through config sections, looks up corresponding plugin classes
        in the registry, instantiates them, and calls onEnvLoad() with the
        section data.
        
        Plugins that don't have a registered class are silently skipped.
        """
        for env_key, plugin_config in self.config.items():
            plugin_cls = PluginMeta._type_registry.get(env_key)
            if plugin_cls:
                plugin = plugin_cls()
                plugin.onEnvLoad(plugin_config)
                self.plugins[env_key] = plugin
    
    def run(self):
        """
        Execute the complete plugin lifecycle.
        
        This method orchestrates the full execution:
        1. Loads all plugins from configuration
        2. Validates all plugins can run (all-or-nothing model)
        3. Starts all plugins in sequence
        4. Enters main loop checking for stop conditions
        5. Shuts down all plugins (guaranteed via finally)
        
        The execution stops when:
        - Any plugin's shouldStop() returns True
        - A KeyboardInterrupt occurs
        - An unhandled exception occurs (after cleanup)
        
        All plugins are guaranteed to have onShutdown() called, even if
        errors occur during startup or execution.
        """
        self.load_plugins()
        
        # If no plugins loaded, nothing to do
        if not self.plugins:
            return
        
        # Check if ALL plugins can run - if any fails, abort entire execution
        if not all(p.canRun(self.config, self) for p in self.plugins.values()):
            return
        
        try:
            # Startup phase - start ALL plugins
            for plugin in self.plugins.values():
                plugin.onStartup(self.config, self)
            
            # Main loop - wait until any plugin says stop
            while True:
                if any(p.shouldStop(self.config, self) for p in self.plugins.values()):
                    break
                time.sleep(1)
                
        finally:
            # Shutdown phase - shutdown ALL plugins
            for plugin in self.plugins.values():
                plugin.onShutdown(self.config, self)


class LDXRunner:
    """
    Configuration manager for LDX plugin execution.
    
    Provides a managed execution environment with:
    - Global configuration merged into all instances
    - Template system for reusable config snippets
    - Custom plugin loading from config directory
    - Automatic path resolution
    
    Configuration Directory: ~/.ldx/runner/configs/
    
    Files:
        - global.toml: Base configuration merged into all instances
        - *.template.toml: Reusable config snippets
        - *.py: Custom plugin implementations
        - *.toml: Instance configurations
    
    Template System:
        Use "template::name" as a string value to inject template content.
        Works at both top-level and nested dictionary levels.
    
    Example Directory Structure:
        ```
        ~/.ldx/runner/configs/
        ├── global.toml          # Shared settings
        ├── game.template.toml   # Reusable game config
        ├── myplugin.py          # Custom plugin
        ├── job1.toml            # Instance config
        └── job2.toml            # Another instance
        ```
    
    Example Usage:
        ```python
        runner = LDXRunner()
        instance = runner.create_instance("job1.toml")
        instance.run()
        ```
    
    Example global.toml:
        ```toml
        [ld]
        close = true
        ```
    
    Example game.template.toml:
        ```toml
        name = "GameEmulator"
        pkg = "com.example.game"
        ```
    
    Example job1.toml:
        ```toml
        [ld]
        # This gets merged: close=true from global, name/pkg from template
        template = "template::game"
        
        [lifetime]
        lifetime = 3600
        ```
    """
    
    def __init__(self):
        """
        Initialize configuration manager.
        
        Creates config directory if needed, loads global config, loads all
        templates, and loads custom plugins from Python files.
        """
        # ~/.ldx/runner/configs
        self.__ldx_dir = Path.home() / ".ldx" / "runner" / "configs"
        self.__ldx_dir.mkdir(parents=True, exist_ok=True)

        # load all the .py files as plugin extensions
        self.load_plugins(self.__ldx_dir)

        # load global.toml
        self.global_config_path = self.__ldx_dir / "global.toml"
        if self.global_config_path.exists():
            with open(self.global_config_path, "r") as f:
                self.global_config = toml.load(f)
        else:
            self.global_config = {}

        # load templates
        self.templates = {}

        for template_file in self.__ldx_dir.glob("*.template.toml"):
            self.load_template(template_file)
    
    def load_template(self, template_path : str):
        """
        Load a template file into the templates registry.
        
        Template name is derived from filename by removing ".template" suffix.
        Example: "game.template.toml" becomes template "game"
        
        Args:
            template_path: Path to template file (string or Path object)
        """
        template_path : Path = Path(template_path)
        template_name = template_path.stem.replace(".template", "")
        with open(template_path, "r") as f:
            template_config = toml.load(f)
        self.templates[template_name] = template_config

    def create_instance(self, config_path : str) -> LDXInstance:
        """
        Create an LDXInstance with merged configuration.
        
        Configuration merging order:
        1. Start with global config (from global.toml)
        2. Overlay instance config (from specified file)
        3. Resolve template references ("template::name" strings)
        
        Template Resolution:
        - Top-level values: "template::game" replaces entire value
        - Nested values: Searches within dict values for template strings
        
        Args:
            config_path: Path to instance config file (absolute or relative to config dir)
        
        Returns:
            Configured LDXInstance ready to run
        
        Example:
            ```python
            runner = LDXRunner()
            instance = runner.create_instance("myjob.toml")
            instance.run()
            ```
        """
        # first check if exists at __ldx_dir
        if not Path(config_path).is_absolute():
            config_path = self.__ldx_dir / config_path

        with open(config_path, "r") as f:
            raw_config = toml.load(f)

        raw_config2 = dict(self.global_config)
        raw_config2.update(raw_config)

        for key, value in raw_config2.items():
            if isinstance(value, str) and value.startswith("template::"):
                template_name = value.split("template::")[1].strip()
                template_config = self.templates.get(template_name)
                if template_config:
                    raw_config2[key] = template_config
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str) and subvalue.startswith("template::"):
                        template_name = subvalue.split("template::")[1].strip()
                        template_config = self.templates.get(template_name)
                        if template_config:
                            raw_config2[key][subkey] = template_config
        return LDXInstance(raw_config2)
    
    def load_plugins(self, plugin_dir : Path):
        """
        Load custom plugin implementations from Python files.
        
        Executes all .py files in the plugin directory. Plugins that inherit
        from LDXPlugin will be automatically registered via the metaclass.
        
        Args:
            plugin_dir: Directory containing custom plugin .py files
        
        Example plugin file (custom_plugin.py):
            ```python
            from ldx.ldx_runner.core.plugin import LDXPlugin
            from dataclasses import dataclass
            
            @dataclass
            class MyPluginModel:
                value: str
            
            class MyPlugin(LDXPlugin):
                __env_key__ = "my_plugin"
                
                def onEnvLoad(self, env):
                    self.model = MyPluginModel(**env)
                
                def onStartup(self, cfg, instance):
                    print(f"Custom plugin: {self.model.value}")
            ```
        
        Warning:
            Uses exec() to load plugins. Only load plugins from trusted sources.
        """
        # use exec method
        for py_file in plugin_dir.glob("*.py"):
            with open(py_file, "r") as f:
                code = f.read()
                exec(code, globals())