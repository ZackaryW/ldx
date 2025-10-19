# Active Context: ldx

## Current Focus
**Status**: Memory bank initialization
**Date**: October 19, 2025
**Phase**: Documentation and project structure establishment

## Recent Changes
1. Initialized memory bank with comprehensive project documentation
2. Documented all 5 major components (ld, ld_cli, ldx, ldx_cli, ldx_server)
3. Captured architecture patterns and design decisions

## Next Steps

### Immediate
1. Create `progress.md` to document current implementation status
2. Identify any gaps between design and implementation
3. Document any active development work

### Short Term
- Expand `ldx_cli` implementation (currently minimal)
- Add comprehensive test coverage
- Set up API documentation generation

### Medium Term
- Implement structured error handling
- Add logging configuration system
- Build example configurations and tutorials

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
If any plugin's `canRun()` returns false, abort entire execution:
```python
if not all(p.canRun(cfg) for p in plugins):
    return  # Don't execute any plugins
```

### 4. Lifecycle Consistency
Same lifecycle in CLI and server modes ensures predictable behavior:
```
onEnvLoad → canRun → onStartup → [loop: shouldStop] → onShutdown
```

### 5. Configuration Management (LDXRunner)
Multi-layered config system with global settings and templates:
- **Global config**: `~/.ldx/runner/configs/global.toml` - base settings for all runs
- **Instance config**: Specific TOML file - overrides global settings
- **Templates**: `*.template.toml` - reusable config snippets referenced via `"template::name"`
- **Merging**: Global → Instance → Template resolution (in that order)

## Learnings and Insights

### About LDPlayer Integration
- LDPlayer console is blocking - operations wait for completion
- Multiple instance management requires careful state tracking
- Batch operations are common use case - designed in from start

### About Plugin Architecture
- Metaclass registration eliminates boilerplate
- Dataclass configs provide type safety and IDE support
- Lifecycle hooks give clear extension points

### About Component Separation
- Clear boundaries between components (ld → ldx → server)
- Optional dependencies enable modular installation
- Each layer adds capabilities without breaking lower layers

### About Configuration
- TOML format is readable and widely supported
- Section keys matching plugin `__env_key__` enables auto-discovery
- Declarative configs reduce need for custom code

## Current Challenges

### 1. ldx_cli Implementation
**Issue**: Minimal implementation - just an empty file
**Impact**: Users can't easily run plugins from CLI
**Consideration**: Design needed for CLI interface to runner

### 2. Error Handling
**Issue**: No structured exception types
**Impact**: Hard to distinguish error types programmatically
**Consideration**: Create exception hierarchy for common failure modes

### 3. Documentation
**Issue**: No API docs or user guides
**Impact**: Steep learning curve for new users
**Consideration**: Add docstring examples and generate docs site

### 4. Testing
**Issue**: Limited test coverage
**Impact**: Harder to refactor with confidence
**Consideration**: Prioritize tests for core Console methods and plugin lifecycle

## User Preferences
- **Shell**: PowerShell (Windows environment)
- **Python Version**: 3.12+
- **Tooling**: Using `uv` for package management
- **File Organization**: Follows minimal implementation principle (see file_org.instructions.md)

## Project Context
- **Version**: 0.1.0 (early development)
- **License**: Defined in LICENSE file
- **Author**: ZackaryW
- **Primary Use Case**: LDPlayer automation for Android app testing/gaming
