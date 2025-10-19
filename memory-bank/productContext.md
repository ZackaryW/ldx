# Product Context: ldx

## Why This Exists
LDPlayer is a popular Android emulator primarily used for gaming and app testing. It provides a console tool (`ldconsole.exe`) for automation, but it has several pain points:

1. **Raw CLI Interface**: The console tool requires direct shell command execution
2. **No Batch Operations**: Managing multiple emulator instances requires repetitive commands
3. **Limited Automation**: No built-in job scheduling or workflow management
4. **Manual Process**: Setting up automation requires custom scripting

ldx solves these problems by providing a comprehensive Python framework that makes LDPlayer automation accessible, repeatable, and scalable.

## Problems Solved

### 1. Console Access Complexity
**Problem**: Users must manually construct shell commands with correct arguments
**Solution**: Python classes with typed methods that map directly to console commands

### 2. Multi-Instance Management
**Problem**: Operating on multiple emulators requires loops and error handling
**Solution**: Batch execution built into the console wrapper - one call, many instances

### 3. Workflow Automation
**Problem**: Complex automation requires custom scripts with lifecycle management
**Solution**: Plugin-based system with defined lifecycle hooks (startup, runtime, shutdown)

### 4. Scheduled Execution
**Problem**: Running automation on schedules requires external tools (cron, Task Scheduler)
**Solution**: Built-in Flask server with APScheduler integration for HTTP-triggered jobs

## How It Works

### Layer 1: Console Wrapper (ld)
```python
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr

console = Console(LDAttr.discover())
console.launch(name="MyEmulator")  # Start an emulator
console.quit(name="MyEmulator")     # Stop it
```

### Layer 2: CLI Interface (ld_cli)
```bash
pyld discover  # Find LDPlayer installation
pyld cmds launch --name MyEmulator
```

### Layer 3: Plugin System (ldx)
```python
# config.toml
[ld]
name = "MyEmulator"
pkg = "com.example.app"

[lifetime]
lifetime = 3600  # Run for 1 hour

# Python execution - Option 1: Direct
from ldx.ldx_runner.core.runner import LDXInstance
import toml
config = toml.load("config.toml")
runner = LDXInstance(config)
runner.run()  # Launches app, waits, then closes

# Python execution - Option 2: With config management
from ldx.ldx_runner.core.runner import LDXRunner
runner = LDXRunner()  # Loads from ~/.ldx/runner/configs
instance = runner.create_instance("myconfig.toml")
instance.run()  # Merges global config + templates, then runs
```

### Layer 4: Server Scheduling (ldx_server)
```python
# Flask server that accepts config via POST
# Schedules execution using APScheduler
# Provides hooks for status monitoring
```

## User Experience Goals

### For Developers
- **Simple**: Import a class, call methods - no subprocess management
- **Typed**: Full type hints for IDE autocomplete and validation
- **Pythonic**: Follows Python conventions and idioms

### For Scripters
- **CLI Ready**: Terminal commands for quick operations
- **Composable**: Pipe and chain commands for complex workflows
- **Discoverable**: Help text and autocomplete for all commands

### For Automation Engineers
- **Plugin System**: Create custom automation by implementing lifecycle hooks
- **Reusable**: Share plugin configurations as TOML files
- **Extensible**: Register custom plugins via metaclass system

### For Operations Teams
- **Server Mode**: Deploy as HTTP service for remote execution
- **Scheduled**: Set up recurring jobs with cron or interval triggers
- **Observable**: Monitor job status and execution history

## Success Criteria
1. A user can control LDPlayer from Python without writing subprocess code
2. Batch operations work reliably across multiple instances
3. Custom automation can be built by writing simple plugin classes
4. Scheduled jobs run unattended with proper error handling
5. The package remains modular - users only install what they need
