# Active Context: ldx

## Current Focus
**Status**: Server infrastructure complete
**Date**: October 22, 2025
**Phase**: Production-ready scheduler with client CLI

## Recent Changes
1. ✅ Decoupled scheduler service from Flask runner
2. ✅ Implemented persistent job registry (JSON at ~/.ldx/server/registry.json)
3. ✅ Created REST API routes for job management
4. ✅ Built complete CLI client (ldx-client) for server interaction
5. ✅ Fixed config loading to support on-demand jobs
6. ✅ Fixed plugin loading order issue in server startup
7. ✅ Fixed scheduler persistence (replaced teardown_appcontext with atexit)

## Next Steps

### Immediate
- Add scenario documentation for server/client usage
- Create example scheduled job configurations
- Add integration tests for server API

### Future Considerations
- Job execution history persistence
- Authentication for server endpoints
- Webhook notifications on job completion

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

### 7. Server Architecture (NEW)
**Components**:
- **SchedulerService**: Decoupled job scheduling and execution
- **JobRegistry**: Persistent storage at ~/.ldx/server/registry.json
- **FlaskLDXRunner**: Thin wrapper loading configs from ~/.ldx/runner/configs/
- **REST API**: Complete CRUD operations for jobs
- **CLI Client**: ldx-client command for remote server interaction

**Job Types**:
- **Scheduled**: Jobs with cron/interval triggers (auto-executed)
- **On-Demand**: Jobs without schedules (triggered via API)

**Execution Model**:
- Each trigger creates timestamped execution_id (e.g., "hello_20251022_145129")
- Execution ID tracks specific runs, base job ID tracks registration
- Status queries use execution_id for triggered jobs

## Key Implementation Details

### Plugin Access Pattern
Plugins stored as dict by env_key allows inter-plugin communication:
```python
instance.plugins["lifetime"].killList.append(("process", "app.exe"))
```

### Scheduler Persistence Pattern
Server uses `atexit.register()` for cleanup, NOT `@app.teardown_appcontext`:
```python
# CORRECT - runs on process termination
atexit.register(lambda: runner.stop())

# WRONG - runs after every request
@app.teardown_appcontext
def stop_scheduler(exception=None):
    runner.stop()  # This stops scheduler after EACH request!
```

### Documentation Status
- ✅ All builtin plugins fully documented
- ✅ Core plugin system fully documented  
- ✅ 4 scenario files created (launch-one, launch-many, use-cli, work-with-kmp)
- ✅ README updated with GitHub links

### Current Gaps
1. **Testing**: Limited coverage for server API
2. **Documentation**: No scenario docs for server/client workflows yet
3. **Authentication**: No auth on server endpoints (future consideration)

## Project Context
- **Version**: 0.1.0
- **Python**: 3.12+
- **Shell**: PowerShell (Windows)
- **Tool**: uv package manager
