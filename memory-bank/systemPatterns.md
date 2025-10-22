# System Patterns: ldx

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                     │
├──────────────┬──────────────┬──────────────┬────────┤
│   Python     │   CLI        │   Config     │  HTTP  │
│   Import     │   (pyld)     │   (TOML)     │  POST  │
└──────┬───────┴──────┬───────┴──────┬───────┴───┬────┘
       │              │               │           │
       ▼              ▼               ▼           ▼
┌─────────────┐ ┌──────────┐  ┌────────────┐ ┌──────────┐
│ ld.Console  │ │ ld_cli   │  │ LDXInstance│ │ FlaskLDX │
│             │ │          │  │            │ │ Runner   │
└──────┬──────┘ └────┬─────┘  └─────┬──────┘ └────┬─────┘
       │             │               │             │
       └─────────────┴───────┬───────┴─────────────┘
                             ▼
                    ┌─────────────────┐
                    │   LDPlayer      │
                    │   ldconsole.exe │
                    └─────────────────┘
```

## Core Design Patterns

### 1. Command Factory Pattern (Console Wrapper)
**Location**: `ldx/ld/console.py`

**Pattern**: Dynamically generate methods from command definitions
```python
for command in SIMPLE_EXEC_LIST:
    setattr(Console, command, _create_simple_exec_method(command))
```

**Why**: 
- Reduces code duplication for similar commands
- Maintains single source of truth for command definitions
- Easy to add new commands by updating enum lists

**Key Components**:
- `SIMPLE_EXEC_LIST`: Commands with no parameters
- `VARIED_EXEC_LIST`: Commands with variable parameters
- `SIMPLE_QUERY_LIST`: Query commands returning output
- `BATCHABLE_COMMANDS`: Commands supporting batch execution

### 2. Batch Execution Mixin
**Location**: `ldx/ld_base/batch_console_ext.py`

**Pattern**: Intercepted `__getattribute__` for automatic batch handling
```python
def __getattribute__(self, name: str):
    if name in BATCHABLE_COMMANDS:
        return batch_wrapper(*args, **kwargs)
```

**Why**:
- Transparent batch execution - same API for single/multi-instance
- Validates parameters before batch execution
- Handles both name-based and index-based targeting

**Batch Call Detection**:
- Checks for `instances` parameter (filter function)
- Checks for `console_func` parameter (custom logic)
- Falls back to standard single-instance execution

### 3. Plugin Registry Metaclass
**Location**: `ldx/ldx_runner/core/plugin.py`

**Pattern**: Automatic plugin registration via metaclass
```python
class PluginMeta(type):
    _type_registry = {}
    
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "LDXPlugin":
            cls._type_registry[new_class.__env_key__] = new_class
        return new_class
```

**Why**:
- No manual registration required
- Plugins auto-register by inheriting from `LDXPlugin`
- Lookup by `__env_key__` matches config file keys

**Plugin Lifecycle**:
1. `onEnvLoad(env)` - Parse configuration into dataclass
2. `canRun(cfg)` - Pre-execution validation
3. `onStartup(cfg)` - Start operations (launch emulator, etc)
4. `shouldStop(cfg)` - Runtime check for termination
5. `onShutdown(cfg)` - Cleanup (close emulator, etc)

### 4. Configuration-Driven Execution
**Location**: `ldx/ldx_runner/core/runner.py`

**Pattern**: TOML config maps to plugin instances
```toml
[ld]
name = "MyEmulator"
pkg = "com.example.app"

[lifetime]
lifetime = 3600
```

**Why**:
- Declarative automation - no code required
- Reusable configurations
- Easy to version control and share

**Execution Flow**:
1. Parse config file (TOML)
2. For each section, lookup plugin by key
3. Instantiate plugin and call `onEnvLoad(section_data)`
4. Check all `canRun()` - abort if any fails
5. Call all `onStartup()` in sequence
6. Loop checking `shouldStop()` until any returns true
7. Call all `onShutdown()` in sequence

**LDXRunner Pattern** (Configuration Manager):
```python
runner = LDXRunner()  # Loads from ~/.ldx/runner/configs
instance = runner.create_instance("myconfig.toml")
instance.run()
```

**Features**:
- Global config: `~/.ldx/runner/configs/global.toml` - merged with all instances
- Templates: `~/.ldx/runner/configs/*.template.toml` - reusable config snippets
- Template references: Use `"template::name"` to inject template values
- Automatic path resolution: Relative paths resolve to config directory

### 5. Decoupled Scheduler Service
**Location**: `ldx/ldx_server/scheduler.py`

**Pattern**: Service layer separated from web layer
```python
class SchedulerService:
    def __init__(self, registry: JobRegistry, max_workers: int = 10):
        self.scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(max_workers)})
        self.registry = registry
        self.job_contexts = {}  # Track execution state
```

**Why**:
- Testable without Flask
- Reusable in other contexts
- Clear separation of concerns

**Design Decision**: Schedule is NOT a plugin
- Plugins define lifecycle behavior (what to do)
- Schedule defines execution timing (when to do it)
- Allows same config to run in CLI (immediate) or server (scheduled)

### 6. Persistent Job Registry
**Location**: `ldx/ldx_server/registry.py`

**Pattern**: JSON-based persistent storage
```python
class JobRegistry:
    def __init__(self, registry_path=Path.home() / ".ldx" / "server" / "registry.json"):
        self._entries: Dict[str, JobRegistryEntry] = {}
        self._load()  # Load from disk on startup
        
    def register(self, job_id, config, schedule, source):
        self._entries[job_id] = JobRegistryEntry(...)
        self._save()  # Persist immediately
```

**Why**:
- Jobs survive server restarts
- Track job metadata (source, execution count, timestamps)
- Separate scheduled from on-demand jobs

**JobRegistryEntry Fields**:
- `job_id`: Unique identifier
- `config`: Full TOML configuration
- `schedule`: ScheduleConfig or None
- `source`: Origin ("api", "config:filename.toml")
- `registered_at`, `last_triggered`, `execution_count`: Tracking data

### 7. Timestamped Execution Tracking
**Location**: `ldx/ldx_server/scheduler.py`

**Pattern**: Separate base job ID from execution ID
```python
def trigger_job(self, job_id: str):
    execution_id = f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Example: "hello_20251022_145129"
    
    context = JobExecutionContext(execution_id, instance)
    self.job_contexts[execution_id] = context  # Track by execution_id
```

**Why**:
- Same job can be triggered multiple times
- Each execution tracked independently
- Query status using execution_id (not base job_id)

**Status Query Pattern**:
```bash
# Trigger returns execution_id
$ ldx-client trigger hello
{"execution_id": "hello_20251022_145129", ...}

# Query using execution_id
$ ldx-client status hello_20251022_145129
{"status": "completed", ...}
```

## Key Architectural Decisions

### 1. Optional Dependencies via Groups
**Decision**: Each component has its own optional dependency group
```toml
[project.optional-dependencies]
ld_cli = ["click>=8.3.0", "psutil>=7.1.0"]
ldx = ["toml>=0.10.2"]
ldx_server = ["apscheduler>=3.11.0", "flask>=3.1.2"]
```

**Rationale**: 
- Users only install what they need
- Core `ld` wrapper has zero dependencies
- Reduces package size and security surface

### 2. Synchronous Execution Model
**Decision**: No async/await, no threading in core logic
**Rationale**:
- LDPlayer console commands are blocking
- Simplifies error handling and debugging
- APScheduler handles concurrency in server mode

### 3. All-or-Nothing Plugin Execution
**Decision**: If any plugin's `canRun()` returns false, abort entire execution
**Rationale**:
- Plugins may depend on each other (e.g., LD launches emulator for other plugins)
- Partial execution leads to undefined states
- Fail fast for clearer error reporting

### 4. Dataclass-Based Configuration
**Decision**: Plugins use dataclasses for config models
```python
@dataclass
class LDModel:
    name: str = None
    index: int = None
```

**Rationale**:
- Type validation built-in
- Self-documenting configuration schema
- IDE autocomplete for config options

## Component Relationships

### Console → CLI
- CLI wraps Console methods with Click decorators
- CLI adds discovery logic for `ldconsole.exe` path
- CLI handles argument parsing and validation

### Console → Runner
- Runner uses Console to control emulators
- LD plugin wraps Console calls in lifecycle hooks
- Runner doesn't directly call Console - delegates to plugins

### Runner → Server
- Server wraps Runner in Flask endpoint handlers
- Server adds APScheduler for timing
- Server executes same plugin lifecycle as CLI runner

## Critical Implementation Paths

### Path 1: Single Instance Launch
```
User → Console.launch(name="X") → open_detached("ldconsole.exe", "launch", "--name", "X")
```

### Path 2: Batch Instance Query
```
User → Console.list2() → query("ldconsole.exe", "list2") → [List2Meta(...), ...]
```

### Path 3: Plugin Execution (Direct)
```
Config Dict → LDXInstance(config) → load_plugins() → PluginMeta._type_registry[key]() → 
plugin.onEnvLoad() → plugin.canRun() → plugin.onStartup() → 
loop(plugin.shouldStop()) → plugin.onShutdown()
```

### Path 3b: Plugin Execution (via LDXRunner)
```
Config File → LDXRunner.create_instance(path) → merge global config → 
resolve templates → LDXInstance(merged_config) → [same as Path 3]
```

### Path 4: Server Startup
```
create_app() → FlaskLDXRunner.__init__() → 
@app.before_request (first request) → runner.start() →
load_configs_from_directory() → [for each .toml] →
create_instance() → load_plugins() → extract_schedule() →
registry.register() → scheduler.schedule_job()
```

### Path 5: Scheduled Job Execution
```
APScheduler trigger → SchedulerService._execute_job(job_id) →
JobExecutionContext → instance.can_run() → 
instance.startup_phase() → instance.execution_phase() →
instance.shutdown_phase() → update context (status, times, error)
```

### Path 6: On-Demand Job Trigger
```
POST /api/scheduler/jobs/{job_id}/trigger →
SchedulerService.trigger_job() → registry.get(job_id) →
registry.create_instance() → generate execution_id (timestamped) →
scheduler.add_job(immediate) → _execute_job(execution_id) →
registry.mark_triggered() → return execution_id
```

### Path 7: Client Query
```
ldx-client status {execution_id} →
GET /api/scheduler/jobs/{execution_id} →
SchedulerService.get_job_status() → job_contexts[execution_id] →
return {status, start_time, end_time, error, plugin_count}
```
