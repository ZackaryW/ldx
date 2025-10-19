# ldx

Control and automate LDPlayer (with possibility of other Android emulators) with Python.

## What is ldx?

ldx is a toolkit for managing LDPlayer emulators. It lets you:

- **Control emulators from Python** - Launch, stop, modify settings
- **Manage multiple instances** - Run commands on many emulators at once
- **Automate tasks** - Create workflows that run automatically
- **Schedule jobs** - Set up recurring automation on a schedule

## Quick Start

**Install for your use case:**

```bash
# Just control emulators from Python
pip install ldx

# Add command-line tools
pip install ldx[ld_cli]

# Add automation system
pip install ldx[ldx]

# Add web server with scheduling
pip install ldx[ldx_server]

# Everything
pip install ldx[ld_cli,ldx,ldx_server]
```

## What Can You Do?

### console controls
[Control One Emulator](docs/scenarios/launch-one.md)

[Control Multiple Emulators](docs/scenarios/launch-many.md)

[Use Command-Line Interface](docs/scenarios/use-cli.md)

### configuration
[Work with Keyboard Mappings](docs/scenarios/work-with-kmp.md)
