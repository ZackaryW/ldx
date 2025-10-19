# Tech Context: ldx

## Technology Stack

### Core Language
- **Python 3.12+**: Required minimum version
- **Type Hints**: Extensive use throughout codebase
- **Dataclasses**: Used for configuration models

### Package Management
- **Build System**: `uv_build` (modern Python packaging)
- **Project File**: `pyproject.toml` (PEP 621 compliant)
- **Dependency Groups**: Optional dependencies via `[project.optional-dependencies]`

### Key Dependencies

#### ld_cli Group
- **click >= 8.3.0**: CLI framework
  - Command decorators and groups
  - Parameter validation
  - Help text generation
- **psutil >= 7.1.0**: Process utilities
  - Process discovery
  - System information

#### ldx Group
- **toml >= 0.10.2**: Configuration parsing
  - Read plugin configurations
  - Parse runner settings

#### ldx_server Group
- **flask >= 3.1.2**: Web framework
  - HTTP endpoints
  - Request handling
- **apscheduler >= 3.11.0**: Job scheduling
  - Cron triggers
  - Interval triggers
- **flask-apscheduler >= 1.13.1**: Flask integration for APScheduler

### Development Tools
- **pytest >= 8.4.2**: Testing framework (dev dependency)
- **ruff**: Linter/formatter (configured to ignore F401 - unused imports)

## Development Setup

### Installation Options

**Minimal (console wrapper only)**:
```bash
pip install ldx
```

**With CLI tools**:
```bash
pip install ldx[ld_cli]
```

**With runner system**:
```bash
pip install ldx[ldx]
```

**With server capabilities**:
```bash
pip install ldx[ldx_server]
```

**Everything**:
```bash
pip install ldx[ld_cli,ldx,ldx_server]
```

**Development**:
```bash
pip install -e .[ld_cli,ldx,ldx_server,dev]
```

### Project Structure Patterns

```
src/ldx/              # Main package
├── __init__.py       # Package root
├── generic/          # Generic utilities (click overrides, config)
├── utils/            # Shared utilities (json, subprocess)
├── ld/               # Console wrapper (core component)
├── ld_base/          # Base classes and models for ld
├── ld_cli/           # CLI interface for ld
├── ld_utils/         # Utilities for ld component
├── ld_ext/           # Extensions for ld (models, objects)
├── ldx_runner/       # Plugin system
│   ├── builtins/     # Built-in plugins
│   ├── core/         # Runner and plugin base
│   └── cli/          # CLI for runner
└── ldx_server/       # Flask server implementation

tests/                # Test files
tests_support/        # Test support modules (plugins for testing)
```

### Entry Points

**Console Script** (defined in pyproject.toml):
```toml
[project.scripts]
pyld = "ldx.ld_cli.__init__:cli"
```

This registers the `pyld` command when package is installed.

## Technical Constraints

### External Dependencies
- **LDPlayer**: Must be installed on system
- **ldconsole.exe**: Console tool must be accessible
- **Windows**: LDPlayer is Windows-only (ldx assumes Windows environment)

### Shell Environment
- **PowerShell**: User's default shell is PowerShell
- **Path Discovery**: Auto-detect `ldconsole.exe` via registry or common paths
- **Subprocess**: Use `open_detached()` for non-blocking commands

### Execution Model
- **Synchronous**: No async/await in core logic
- **Blocking**: Console commands are blocking operations
- **Thread Pool**: APScheduler uses ThreadPoolExecutor in server mode

### Python Specifics
- **Metaclasses**: Plugin registration uses metaclass pattern
- **Type Annotations**: Heavy use of `typing` module for IDE support
- **Dataclasses**: Configuration models use `@dataclass` decorator

## Tool Usage Patterns

### Subprocess Management
**Location**: `ldx/utils/subprocess.py`

**Pattern**: Wrapper functions for subprocess calls
```python
def open_detached(exe, *args):
    # Non-blocking command execution
    subprocess.Popen([exe, *args], ...)

def query(exe, *args):
    # Blocking command with output capture
    subprocess.run([exe, *args], capture_output=True)
```

**Why**: Centralized subprocess handling with consistent error handling

### Configuration Loading
**Pattern**: TOML files map to plugin instances
```python
import toml
config = toml.load("config.toml")
# Each section key maps to a plugin via __env_key__
```

**LDXRunner Config Management**:
- **Config Directory**: `~/.ldx/runner/configs/`
- **Global Config**: `global.toml` - merged into all instance configs
- **Templates**: `*.template.toml` - reusable snippets
- **Template Reference**: String value `"template::name"` gets replaced with template content
- **Path Resolution**: Relative paths resolve to config directory

### Logging
**Current State**: Uses Python's `logging` module
**Pattern**: `logging.info()` for execution tracking
**Note**: No structured logging framework configured yet

### Testing
**Framework**: pytest
**Location**: `tests/` directory
**Support**: Test plugins in `tests_support/test_plugins.py`

## Environment Variables

### LD_CONSOLE_PATH
**Purpose**: Override auto-detection of `ldconsole.exe` path
**Usage**: 
```bash
export LD_CONSOLE_PATH="/path/to/ldconsole.exe"
pyld cmds launch --name MyEmulator
```

**Context Object**: Passed via Click's context
```python
@click.pass_context
def cli(ctx: click.Context, ldconsole_path):
    ctx.obj['ldconsole_path'] = ldconsole_path
```

## Configuration Files

### pyproject.toml
**Purpose**: Project metadata, dependencies, build config
**Key Sections**:
- `[project]`: Package metadata
- `[project.scripts]`: Entry points
- `[project.optional-dependencies]`: Feature groups
- `[build-system]`: Build backend config
- `[tool.ruff]`: Linter configuration

### Plugin Config (TOML)
**Format**: Section per plugin
```toml
[plugin_env_key]
param1 = "value"
param2 = 123
```

**Loading**: Each section passed to matching plugin's `onEnvLoad()`

## Build and Distribution

### Build Backend
- **System**: uv_build >= 0.8.22, < 0.9.0
- **Output**: Wheel and sdist packages

### Version Management
- **Current**: 0.1.0
- **Strategy**: Semantic versioning

### Distribution Strategy
- **PyPI**: Intended distribution platform
- **Installation**: via pip/uv/poetry

## Known Technical Debt
1. **ldx_cli**: Minimal implementation - CLI for runner not fully built
2. **Error Handling**: No structured error types or exception hierarchy
3. **Logging**: Basic logging, no log levels configuration
4. **Testing**: Limited test coverage
5. **Documentation**: No API documentation generation setup
