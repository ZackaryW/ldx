# Launch One Emulator

**Goal:** Control a single LDPlayer emulator from Python.

## Basic Setup

```python
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr

# Auto-find LDPlayer
console = Console(LDAttr.discover())
```

## Launch Emulator

**By name:**
```python
console.launch(name="MyEmulator")
```

**By index:**
```python
console.launch(index=0)
```

**With specific app:**
```python
console.launchex(name="MyEmulator", packagename="com.example.app")
```

## Stop Emulator

```python
console.quit(name="MyEmulator")
```

## Get Info

```python
emulators = console.list2()

for emu in emulators:
    print(f"{emu.name}: {'running' if emu.running else 'stopped'}")
```

## Change Settings

**Resolution:**
```python
console.modify(name="MyEmulator", resolution="1920x1080")
```

**CPU and Memory:**
```python
console.modify(name="MyEmulator", cpu=4, memory=4096)
```

**Multiple settings:**
```python
console.modify(
    name="MyEmulator",
    resolution="1920x1080",
    cpu=4,
    memory=4096,
    root=True
)
```

## Complete Example

```python
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr
import time

console = Console(LDAttr.discover())

# Launch
console.launch(name="MyEmulator")
print("Launching...")
time.sleep(30)

# Check status
emulators = console.list2()
target = next(e for e in emulators if e.name == "MyEmulator")
print(f"Status: {target.running}")

# Stop
console.quit(name="MyEmulator")
print("Stopped")
```
