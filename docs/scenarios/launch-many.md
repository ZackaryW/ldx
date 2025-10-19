# Control Multiple Emulators

**Goal:** Run commands on many emulators at once.

## Basic Setup

```python
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr

console = Console(LDAttr.discover())
```

## Batch Launch

**Launch all:**
```python
console.launch(instances=lambda m: True)
```

**Launch by name pattern:**
```python
console.launch(instances=lambda m: m.name.startswith("Test"))
```

**Launch stopped ones:**
```python
console.launch(instances=lambda m: not m.running)
```

## Batch Stop

**Stop all running:**
```python
console.quit(instances=lambda m: m.running)
```

**Or use shortcut:**
```python
console.quitall()
```

## Filter Patterns

**By name:**
```python
# Contains text
console.launch(instances=lambda m: "Game" in m.name)

# Starts with
console.launch(instances=lambda m: m.name.startswith("Farm"))

# Ends with
console.launch(instances=lambda m: m.name.endswith("_1"))
```

**By index:**
```python
# First 5
console.launch(instances=lambda m: m.index < 5)

# Range
console.launch(instances=lambda m: 3 <= m.index <= 7)
```

**Multiple conditions:**
```python
console.launch(instances=lambda m: 
    m.name.startswith("Test") and not m.running
)
```

## Batch Modify

```python
# Set resolution for all Test emulators
console.modify(
    instances=lambda m: m.name.startswith("Test"),
    resolution="1920x1080"
)
```

## Complete Example

```python
from ldx.ld.console import Console
from ldx.ld.ldattr import LDAttr

console = Console(LDAttr.discover())

# Get all emulators
emulators = console.list2()
print(f"Total: {len(emulators)}")

# Stop all running
console.quit(instances=lambda m: m.running)
print("Stopped all")

# Launch test group
console.launch(instances=lambda m: m.name.startswith("Test"))
print("Test group launched")
```
