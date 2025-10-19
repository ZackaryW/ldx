from pathlib import Path
import time
from .plugin import LDXPlugin, PluginMeta
import toml

class LDXInstance:
    """
    Simple synchronous runner for CLI usage.
    Executes plugins immediately without scheduling.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.plugins : dict[str, LDXPlugin] = {}
    
    def load_plugins(self):
        """Load and instantiate plugins from config"""
        for env_key, plugin_config in self.config.items():
            plugin_cls = PluginMeta._type_registry.get(env_key)
            if plugin_cls:
                plugin = plugin_cls()
                plugin.onEnvLoad(plugin_config)
                self.plugins[env_key] = plugin
    
    def run(self):
        """Execute the plugin lifecycle"""
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
    def __init__(self):
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
        template_path : Path = Path(template_path)
        template_name = template_path.stem.replace(".template", "")
        with open(template_path, "r") as f:
            template_config = toml.load(f)
        self.templates[template_name] = template_config

    def create_instance(self, config_path : str) -> LDXInstance:
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
        # use exec method
        for py_file in plugin_dir.glob("*.py"):
            with open(py_file, "r") as f:
                code = f.read()
                exec(code, globals())