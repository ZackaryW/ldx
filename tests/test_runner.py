"""
Test cases for LDXInstance.
Tests the atomic config execution model and plugin lifecycle.
"""
import pytest
import time
from ldx.ldx_runner.core.runner import LDXInstance
from ldx.ldx_runner.core.plugin import PluginMeta


@pytest.fixture(autouse=True)
def reset_plugin_registry():
    """Reset the plugin registry before and after each test"""
    # Save original registry
    original_registry = PluginMeta._type_registry.copy()
    
    # Clear it for the test
    PluginMeta._type_registry.clear()
    
    yield
    
    # Restore original registry after test
    PluginMeta._type_registry.clear()
    PluginMeta._type_registry.update(original_registry)


def test_single_plugin_execution():
    """Test basic execution with a single plugin"""
    from tests_support.test_plugins import TimedPlugin
    
    config = {
        "timed": {
            "duration": 1
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Verify plugin was started and stopped
    plugin = runner.plugins[0]
    assert plugin.started is True
    assert plugin.stopped is True


def test_multiple_plugins_execution():
    """Test execution with multiple plugins"""
    from tests_support.test_plugins import SimplePlugin, TimedPlugin
    
    config = {
        "simple": {
            "value": "test",
            "lifetime": 2
        },
        "timed": {
            "duration": 1
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Both plugins should have started and stopped
    # Should stop after 1 second (timed plugin stops first)
    assert len(runner.plugins) == 2
    for plugin in runner.plugins:
        assert plugin.started is True
        assert plugin.stopped is True


def test_atomic_execution_all_must_canrun():
    """Test that ALL plugins must return True for canRun()"""
    from tests_support.test_plugins import SimplePlugin, CannotRunPlugin
    
    config = {
        "simple": {
            "value": "test",
            "lifetime": 2
        },
        "cannot_run": {
            "can_run": False
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Neither plugin should have started because one failed canRun()
    for plugin in runner.plugins:
        assert plugin.started is False
        assert plugin.stopped is False


def test_atomic_execution_all_can_run():
    """Test that when ALL plugins pass canRun(), execution proceeds"""
    from tests_support.test_plugins import SimplePlugin, CannotRunPlugin, TimedPlugin
    
    config = {
        "simple": {
            "value": "test",
            "lifetime": 2
        },
        "cannot_run": {
            "can_run": True  # This time it CAN run
        },
        "timed": {
            "duration": 1
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # All plugins should have started and stopped
    assert len(runner.plugins) == 3
    for plugin in runner.plugins:
        assert plugin.started is True
        assert plugin.stopped is True


def test_stop_on_any_plugin_shouldstop():
    """Test that loop stops when ANY plugin returns True for shouldStop()"""
    from tests_support.test_plugins import CounterPlugin, SimplePlugin
    
    config = {
        "counter": {
            "max_count": 3
        },
        "simple": {
            "value": "test",
            "lifetime": 10  # Won't reach this - counter stops first
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Counter plugin should have stopped after 3 iterations
    counter_plugin = next(p for p in runner.plugins if p.__env_key__ == "counter")
    assert counter_plugin.count == 3
    
    # Both plugins should have gone through full lifecycle
    for plugin in runner.plugins:
        assert plugin.started is True
        assert plugin.stopped is True


def test_lifecycle_order():
    """Test that lifecycle methods are called in correct order"""
    from tests_support.test_plugins import LifecycleTrackerPlugin
    
    config = {
        "lifecycle_tracker": {}
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    plugin = runner.plugins[0]
    expected_calls = [
        "onEnvLoad",
        "canRun",
        "onStartup",
        "shouldStop",
        "shouldStop",  # Called twice before stopping
        "onShutdown"
    ]
    
    assert plugin.lifecycle_calls == expected_calls


def test_shutdown_called_even_on_startup_error():
    """Test that onShutdown is called even when onStartup raises an error"""
    from tests_support.test_plugins import ErrorPlugin, SimplePlugin
    
    config = {
        "error": {
            "error_on": "startup"
        },
        "simple": {
            "value": "test",
            "lifetime": 2
        }
    }
    
    runner = LDXInstance(config)
    
    # Should raise error but still call shutdown
    with pytest.raises(RuntimeError, match="Simulated startup error"):
        runner.run()
    
    # onShutdown should still be called on all plugins (finally block)
    for plugin in runner.plugins:
        assert plugin.stopped is True


def test_multiple_timed_plugins():
    """Test multiple timed plugins with different durations"""
    from tests_support.test_plugins import TimedPlugin
    
    # Register multiple instances manually since they share __env_key__
    class FastTimedPlugin(TimedPlugin):
        __env_key__ = "fast_timed"
    
    class SlowTimedPlugin(TimedPlugin):
        __env_key__ = "slow_timed"
    
    config = {
        "fast_timed": {
            "duration": 1
        },
        "slow_timed": {
            "duration": 3
        }
    }
    
    start_time = time.time()
    runner = LDXInstance(config)
    runner.run()
    elapsed = time.time() - start_time
    
    # Should stop when FIRST plugin (fast_timed) says stop
    assert elapsed < 2  # Should be around 1 second, not 3
    
    # Both should have been started and stopped
    for plugin in runner.plugins:
        assert plugin.started is True
        assert plugin.stopped is True


def test_empty_config():
    """Test runner with empty config"""
    config = {}
    
    runner = LDXInstance(config)
    runner.run()
    
    # Should complete without error
    assert len(runner.plugins) == 0


def test_config_with_unknown_plugins():
    """Test config with keys that don't match any plugin"""
    config = {
        "unknown_plugin": {
            "some": "value"
        },
        "another_unknown": {
            "other": "value"
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Should skip unknown plugins
    assert len(runner.plugins) == 0


def test_plugin_env_load():
    """Test that plugins receive their configuration correctly"""
    from tests_support.test_plugins import SimplePlugin
    
    config = {
        "simple": {
            "value": "custom_value",
            "lifetime": 1
        }
    }
    
    runner = LDXInstance(config)
    runner.load_plugins()
    
    plugin = runner.plugins[0]
    assert plugin.model.value == "custom_value"
    assert plugin.model.lifetime == 1


def test_counter_plugin_iterations():
    """Test that shouldStop is called repeatedly in loop"""
    from tests_support.test_plugins import CounterPlugin
    
    config = {
        "counter": {
            "max_count": 10
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    plugin = runner.plugins[0]
    assert plugin.count == 10


def test_all_plugins_started_before_loop():
    """Test that ALL plugins onStartup is called before entering loop"""
    from tests_support.test_plugins import LifecycleTrackerPlugin
    
    # Create multiple tracker instances
    class Tracker1(LifecycleTrackerPlugin):
        __env_key__ = "tracker1"
    
    class Tracker2(LifecycleTrackerPlugin):
        __env_key__ = "tracker2"
    
    config = {
        "tracker1": {},
        "tracker2": {}
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # Both trackers should have onStartup before any shouldStop
    for plugin in runner.plugins:
        startup_idx = plugin.lifecycle_calls.index("onStartup")
        first_shouldstop_idx = plugin.lifecycle_calls.index("shouldStop")
        assert startup_idx < first_shouldstop_idx


def test_all_plugins_shutdown_called():
    """Test that onShutdown is called on ALL plugins"""
    from tests_support.test_plugins import SimplePlugin, TimedPlugin, CounterPlugin
    
    config = {
        "simple": {
            "value": "test",
            "lifetime": 10  # Won't reach
        },
        "timed": {
            "duration": 10  # Won't reach
        },
        "counter": {
            "max_count": 2  # This stops first
        }
    }
    
    runner = LDXInstance(config)
    runner.run()
    
    # All plugins must have shutdown called
    assert len(runner.plugins) == 3
    for plugin in runner.plugins:
        assert plugin.stopped is True
