# ldx

Control and automate LDPlayer (with possibility of other Android emulators) with Python.

## What is ldx?

ldx is a complete automation toolkit for managing LDPlayer emulators. It lets you:

- **Control emulators from Python** - Launch, stop, modify settings
- **Manage multiple instances** - Run commands on many emulators at once
- **Automate tasks** - Create workflows with plugin-based lifecycle hooks
- **Schedule jobs** - Set up recurring automation with cron/interval triggers
- **Remote management** - Deploy as HTTP server with REST API
- **Track executions** - Monitor job status and execution history

## Quick Start

**Install for your use case:**

```bash
# Just control emulators from Python
pip install ldx

# Add command-line tools
pip install ldx[ld_cli]

# Add automation system (plugins)
pip install ldx[ldx]

# Add web server with scheduling
pip install ldx[ldx_server]

# Add client CLI for server
pip install ldx[ldx_client]

# Everything
pip install ldx[ld_cli,ldx,ldx_server,ldx_client]
```

## What Can You Do?

### Console Controls
- [Control One Emulator](https://github.com/ZackaryW/ldx/blob/main/docs/scenarios/launch-one.md)
- [Control Multiple Emulators](https://github.com/ZackaryW/ldx/blob/main/docs/scenarios/launch-many.md)
- [Use Command-Line Interface](https://github.com/ZackaryW/ldx/blob/main/docs/scenarios/use-cli.md)

### Configuration
- [Work with Keyboard Mappings](https://github.com/ZackaryW/ldx/blob/main/docs/scenarios/work-with-kmp.md)

### Automation System

**Create plugin-based automation:**
```toml
# config.toml
[ld]
name = "GameEmulator"
pkg = "com.example.game"

[lifetime]
lifetime = 3600  # Run for 1 hour
```

**Execute directly:**
```python
from ldx.ldx_runner.core.runner import LDXInstance
import toml

config = toml.load("config.toml")
runner = LDXInstance(config)
runner.run()  # Launches app, waits, then closes
```

### Server & Scheduling

**Start server (auto-loads configs from ~/.ldx/runner/configs/):**
```bash
uv run ldx server
```

**Use client CLI:**
```bash
# List registered jobs
ldx-client list registry

# Trigger on-demand job
ldx-client trigger hello
# Returns: {"execution_id": "hello_20251022_145129", ...}

# Check execution status
ldx-client status hello_20251022_145129

# List active executions
ldx-client list active
```

**Scheduled jobs (add [schedule] section to config):**
```toml
[ld]
name = "DailyTask"

[lifetime]
lifetime = 600

[schedule]
trigger = "cron"
hour = 10
minute = 30
# Runs daily at 10:30 AM
```

### Key Features

- **Auto-loading**: Place .toml files in `~/.ldx/runner/configs/`, server loads them automatically
- **Persistent registry**: Jobs survive server restarts (stored in `~/.ldx/server/registry.json`)
- **Execution tracking**: Each trigger creates timestamped execution ID for independent tracking
- **Job types**:
  - **Scheduled**: With `[schedule]` section - runs automatically
  - **On-demand**: Without `[schedule]` - triggered via API
- **REST API**: Complete CRUD operations for job management
- **CLI client**: Remote control with color-coded output
