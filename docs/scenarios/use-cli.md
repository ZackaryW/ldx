# Use Command-Line Interface

**Goal:** Control LDPlayer emulators using the `pyld` terminal command.

## Basic Setup

```bash
# Auto-discover LDPlayer installation
pyld discover

# Check version
pyld --version
```

## Launch Emulator

**By name:**
```bash
pyld console launch --name "MyEmulator"
```

**By index:**
```bash
pyld console launch --index 0
```

**Launch app directly:**
```bash
pyld console launchex --name "MyEmulator" --packagename "com.example.app"
```

## Stop Emulator

```bash
pyld console quit --name "MyEmulator"
```

**Stop all running:**
```bash
pyld console quitall
```

## Query Information

**List all emulators:**
```bash
pyld console list2
```

**Check if running:**
```bash
pyld console isrunning --name "MyEmulator"
```

**List running only:**
```bash
pyld console runninglist
```

## Batch Operations

**Launch by pattern:**
```bash
pyld console launch --batch-starts "Test"
```

**Stop by pattern:**
```bash
pyld console quit --batch-starts "Farm"
```

**Launch by list:**
```bash
pyld console launch --batch-list "Emu1,Emu2,Emu3"
```

## App Management

**Install app:**
```bash
pyld console installapp --name "MyEmulator" --filename "app.apk"
```

**Run app:**
```bash
pyld console runapp --name "MyEmulator" --packagename "com.example.app"
```

**Kill app:**
```bash
pyld console killapp --name "MyEmulator" --packagename "com.example.app"
```

**Uninstall app:**
```bash
pyld console uninstallapp --name "MyEmulator" --packagename "com.example.app"
```

## Configuration

**Modify resolution:**
```bash
pyld console modify --name "MyEmulator" --resolution "1920x1080"
```

**Modify CPU and memory:**
```bash
pyld console modify --name "MyEmulator" --cpu 4 --memory 4096
```

**Set properties:**
```bash
pyld console setprop --name "MyEmulator" --key "debug.mode" --value "true"
```

**Get property:**
```bash
pyld console getprop --name "MyEmulator" --key "ro.build.version"
```

## Complete Example

```bash
# Discover LDPlayer
pyld discover

# Check available emulators
pyld console list2

# Launch specific emulator
pyld console launch --name "TestDevice"

# Wait for boot (do other things)

# Check if running
pyld console isrunning --name "TestDevice"

# Run an app
pyld console runapp --name "TestDevice" --packagename "com.example.game"

# Later: stop it
pyld console quit --name "TestDevice"
```
