# Project Brief: ldx

## Overview
ldx is a modular Python package designed for LDPlayer (Android emulator) automation and management. It provides a comprehensive framework for controlling LDPlayer instances through console commands, CLI tools, and a plugin-based automation system with optional scheduling capabilities.

## Core Components

### 1. ld - Console Wrapper
- **Purpose**: Pythonic wrapper around LDPlayer's console (`ldconsole.exe`)
- **Key Feature**: Batchable operations - execute commands across multiple emulator instances
- **Entry Point**: `ldx.ld.console.Console` class
- **Dependencies**: Base package only (no optional deps)

### 2. ld_cli - CLI Interface
- **Purpose**: Click-based command-line interface for ld wrapper
- **Key Feature**: Exposes console operations through terminal commands
- **Entry Point**: `pyld` command (defined in pyproject.toml)
- **Dependencies**: Requires `ld_cli` optional group (click, psutil)

### 3. ldx - Plugin Runner System
- **Purpose**: Event-driven plugin system for automation workflows
- **Key Feature**: Lifecycle-based execution (onEnvLoad → onStartup → shouldStop → onShutdown)
- **Entry Point**: `ldx.ldx_runner.core.runner.LDXInstance`
- **Dependencies**: Requires `ldx` optional group (toml)

### 4. ldx_cli - Runner CLI (Planned/Minimal)
- **Purpose**: Click interface for ldx runner
- **Current Status**: Minimal implementation in `ldx_runner/cli/main.py`
- **Dependencies**: Would extend `ld_cli` dependencies

### 5. ldx_server - Flask Scheduler
- **Purpose**: HTTP server with APScheduler integration for remote execution
- **Key Feature**: Schedule automation jobs via POST requests and webhooks
- **Entry Point**: `ldx.ldx_server.flask_runner.FlaskLDXRunner`
- **Dependencies**: Requires `ldx_server` optional group (flask, flask-apscheduler)

## Technical Architecture

### Package Structure
```
src/ldx/
├── ld/              # Core console wrapper
├── ld_cli/          # CLI for console
├── ldx_runner/      # Plugin system
│   ├── builtins/    # Built-in plugins (ld, lifetime, schedule)
│   ├── core/        # Runner & plugin base classes
│   └── cli/         # Runner CLI (minimal)
└── ldx_server/      # Flask server implementation
```

### Dependency Model
- **Optional Dependencies**: Each major component has its own optional group
- **Modular Installation**: Users can install only what they need
- **Build System**: Uses `uv_build` (modern Python packaging)

## Requirements
- Python >= 3.12
- LDPlayer installation (for console operations)
- Optional: Flask/APScheduler for server mode
- Optional: Click for CLI interfaces

## Goals
1. Provide simple, Pythonic access to LDPlayer console commands
2. Enable batch operations across multiple emulator instances
3. Support flexible automation through plugin-based architecture
4. Allow both CLI and server-based execution modes
5. Maintain modular, optional dependencies for lightweight installations
