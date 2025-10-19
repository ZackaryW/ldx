# Active Context: ldx

## Current Focus
**Status**: Documentation phase complete
**Date**: October 19, 2025
**Phase**: Core implementation stable with comprehensive docstrings

## Recent Changes
1. ✅ Added comprehensive docstrings to all builtin plugins (ld, lifetime, mxx, os)
2. ✅ Added full documentation to core plugin system (plugin.py, runner.py)
3. ✅ Created 4 scenario documents with GitHub links
4. ✅ Updated LDXInstance to use dict for plugins (was list)
5. ✅ Plugin lifecycle methods now receive `instance` parameter
6. ✅ LDXRunner supports custom plugin loading from .py files

## Next Steps

### Immediate
- Implement ldx_cli for running plugins from command line
- Add basic test coverage for plugin lifecycle
- Create example configuration files

### Short Term
- Structured logging implementation
- Error handling improvements
- Generate API docs from docstrings

## Active Decisions

### Plugin System Design
**Decision**: Schedule is NOT a plugin - it's metadata
**Reasoning**: 
- Plugins define *what* to do (behavior)
- Schedule defines *when* to do it (timing)
- Keeps concerns separated
- Allows same config to run in CLI or server mode

**Implementation**:
- `ScheduleConfig` dataclass for schedule metadata
- Runner/Server interprets schedule separately from plugins
- Plugins remain unaware of scheduling

### Batch Execution Model
**Decision**: Use `__getattribute__` interception for transparent batching
**Trade-offs**:
- **Pro**: Same API for single and batch operations
- **Pro**: No need for separate batch methods
- **Con**: Magic behavior may be non-obvious
- **Con**: Slightly more complex implementation

**Pattern**:
```python
# Single instance
console.launch(name="X")

# Batch - same method, different params
console.launch(instances=lambda m: m.name.startswith("Test"))
```

### Dependency Strategy
**Decision**: Optional dependency groups
**Impact**:
- Core package has zero dependencies
- Users only install what they need
- More complex installation documentation
- Better for security and package size

## Important Patterns

### 1. Command Factory Pattern
Dynamically create methods from command definitions to reduce duplication:
```python
for command in SIMPLE_EXEC_LIST:
    setattr(Console, command, _create_simple_exec_method(command))
```

### 2. Plugin Registry Metaclass
Automatic plugin registration on class definition:
```python
class MyPlugin(LDXPlugin):
    __env_key__ = "my_plugin"
    # Automatically registered in PluginMeta._type_registry
```

### 3. All-or-Nothing Execution
If any plugin's `canRun()` returns false, abort entire execution

### 4. Lifecycle Consistency
Same lifecycle: `onEnvLoad → canRun → onStartup → [loop: shouldStop] → onShutdown`

### 5. Configuration Management (LDXRunner)
- Global config: `~/.ldx/runner/configs/global.toml`
- Templates: `*.template.toml` - referenced via `"template::name"`
- Custom plugins: Load .py files from config directory
- Merging: Global → Instance → Template resolution

### 6. Instance Parameter in Lifecycle
Plugin methods receive `instance` parameter to access other plugins:
```python
def onStartup(self, cfg, instance):
    lifetime = instance.plugins.get("lifetime")
```

## Key Implementation Details

### Plugin Access Pattern
Plugins stored as dict by env_key allows inter-plugin communication:
```python
instance.plugins["lifetime"].killList.append(("process", "app.exe"))
```

### Documentation Status
- ✅ All builtin plugins fully documented
- ✅ Core plugin system fully documented  
- ✅ 4 scenario files created (launch-one, launch-many, use-cli, work-with-kmp)
- ✅ README updated with GitHub links

### Current Gaps
1. **ldx_cli**: Empty implementation file
2. **Testing**: Limited coverage
3. **Logging**: Basic only
4. **Error Handling**: No custom exceptions

## Project Context
- **Version**: 0.1.0
- **Python**: 3.12+
- **Shell**: PowerShell (Windows)
- **Tool**: uv package manager
