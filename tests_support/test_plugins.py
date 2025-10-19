"""
Test plugins for LDXRunner testing.
These plugins simulate various behaviors for comprehensive testing.
"""
from dataclasses import dataclass
from ldx.ldx_runner.core.plugin import LDXPlugin


@dataclass
class SimplePluginModel:
    value: str = "default"
    lifetime: int = 2  # Default 2 seconds


class SimplePlugin(LDXPlugin):
    """Basic plugin that uses lifetime to stop"""
    __env_key__ = "simple"
    
    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
        self.start_time = None
    
    def onEnvLoad(self, env):
        self.model = SimplePluginModel(**env)
    
    def onStartup(self, cfg, instance):
        import time
        self.started = True
        self.start_time = time.time()
    
    def shouldStop(self, cfg, instance):
        if self.start_time is None:
            return False
        import time
        elapsed = time.time() - self.start_time
        return elapsed >= self.model.lifetime
    
    def onShutdown(self, cfg, instance):
        self.stopped = True


@dataclass
class TimedPluginModel:
    duration: int = 3  # seconds


class TimedPlugin(LDXPlugin):
    """Plugin that stops after a specified duration"""
    __env_key__ = "timed"
    
    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
        self.start_time = None
    
    def onEnvLoad(self, env):
        self.model = TimedPluginModel(**env)
    
    def onStartup(self, cfg, instance):
        import time
        self.started = True
        self.start_time = time.time()
    
    def shouldStop(self, cfg, instance):
        if self.start_time is None:
            return False
        import time
        elapsed = time.time() - self.start_time
        return elapsed >= self.model.duration
    
    def onShutdown(self, cfg, instance):
        self.stopped = True


@dataclass
class CannotRunPluginModel:
    can_run: bool = False


class CannotRunPlugin(LDXPlugin):
    """Plugin that fails canRun() check"""
    __env_key__ = "cannot_run"
    
    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
    
    def onEnvLoad(self, env):
        self.model = CannotRunPluginModel(**env)
    
    def canRun(self, cfg, instance):
        return self.model.can_run
    
    def onStartup(self, cfg, instance):
        self.started = True
    
    def onShutdown(self, cfg, instance):
        self.stopped = True


@dataclass
class CounterPluginModel:
    max_count: int = 5


class CounterPlugin(LDXPlugin):
    """Plugin that counts iterations and stops"""
    __env_key__ = "counter"
    
    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
        self.count = 0
    
    def onEnvLoad(self, env):
        self.model = CounterPluginModel(**env)
    
    def onStartup(self, cfg, instance):
        self.started = True
        self.count = 0
    
    def shouldStop(self, cfg, instance):
        self.count += 1
        return self.count >= self.model.max_count
    
    def onShutdown(self, cfg, instance):
        self.stopped = True


@dataclass
class LifecycleTrackerModel:
    pass


class LifecycleTrackerPlugin(LDXPlugin):
    """Plugin that tracks all lifecycle calls"""
    __env_key__ = "lifecycle_tracker"
    
    def __init__(self):
        super().__init__()
        self.lifecycle_calls = []
    
    def onEnvLoad(self, env):
        self.model = LifecycleTrackerModel(**env)
        self.lifecycle_calls.append("onEnvLoad")
    
    def canRun(self, cfg, instance):
        self.lifecycle_calls.append("canRun")
        return True
    
    def onStartup(self, cfg, instance):
        self.lifecycle_calls.append("onStartup")
    
    def shouldStop(self, cfg, instance):
        self.lifecycle_calls.append("shouldStop")
        # Stop after 2 checks
        return self.lifecycle_calls.count("shouldStop") >= 2
    
    def onShutdown(self, cfg, instance):
        self.lifecycle_calls.append("onShutdown")


@dataclass
class ErrorPluginModel:
    error_on: str = None  # "startup", "shutdown", or None


class ErrorPlugin(LDXPlugin):
    """Plugin that can throw errors at different lifecycle stages"""
    __env_key__ = "error"
    
    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
    
    def onEnvLoad(self, env):
        self.model = ErrorPluginModel(**env)
    
    def onStartup(self, cfg, instance):
        if self.model.error_on == "startup":
            raise RuntimeError("Simulated startup error")
        self.started = True
    
    def onShutdown(self, cfg, instance):
        if self.model.error_on == "shutdown":
            raise RuntimeError("Simulated shutdown error")
        self.stopped = True
