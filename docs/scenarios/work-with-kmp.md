# Work with Keyboard Mappings

**Goal:** Load, modify, and save LDPlayer keyboard mapping (KMP) files.

## Basic Setup

```python
from ldx.ld.ldattr import LDAttr
from ldx.ld_ext.object.kmp import KMPFile

# Initialize with LDPlayer path
kmp_file = KMPFile(LDAttr.discover())
```

## List Available Mappings

**List custom mappings:**
```python
custom_list = kmp_file.customizeList()
print(custom_list)  # ['mygame.kmp', 'shooter.kmp']
```

## Load Mappings

**Load custom mapping:**
```python
mapping = kmp_file.getCustomize("mygame")
# or with extension
mapping = kmp_file.getCustomize("mygame.kmp")
```

**Load recommended mapping:**
```python
mapping = kmp_file.getRecommended("pubg")
```

**Load from any path:**
```python
mapping = KMPFile.load("C:/path/to/custom.kmp")
```

## Read Mapping Data

**Access configuration info:**
```python
print(mapping.configInfo.packageNamePattern)
print(mapping.configInfo.resolutionPattern.width)
print(mapping.configInfo.resolutionPattern.height)
```

**Access keyboard config:**
```python
print(mapping.keyboardConfig.mouseCenter.x)
print(mapping.keyboardConfig.mouseCenter.y)
print(mapping.keyboardConfig.cursor)
```

**List key mappings:**
```python
for entry in mapping.keyboardMappings:
    print(f"Key: {entry.data.key}")
    print(f"Position: ({entry.data.point.x}, {entry.data.point.y})")
```

## Modify Mappings

**Change resolution pattern:**
```python
mapping.configInfo.resolutionPattern.width = 1920
mapping.configInfo.resolutionPattern.height = 1080
```

**Update package name:**
```python
mapping.configInfo.packageNamePattern = "com.example.newgame"
```

**Modify key position:**
```python
mapping.keyboardMappings[0].data.point.x = 500
mapping.keyboardMappings[0].data.point.y = 300
```

**Add new key mapping:**
```python
from ldx.ld_ext.model.kmp import KeyboardEntry, KeyboardPointData, Point

new_mapping = KeyboardEntry(
    class_name="com.xd.screencontrol.screentouch.PointTouch",
    data=KeyboardPointData(
        key=65,  # 'A' key
        secondKey=0,
        point=Point(x=100, y=200),
        description="Jump"
    )
)
mapping.keyboardMappings.append(new_mapping)
```

## Save Mappings

**Save to custom configs:**
```python
kmp_file.dump("modified.kmp", mapping)
```

**Save to absolute path:**
```python
kmp_file.dump("C:/backups/game_config.kmp", mapping)
```

## Complete Example

```python
from ldx.ld.ldattr import LDAttr
from ldx.ld_ext.object.kmp import KMPFile
from ldx.ld_ext.model.kmp import Point

# Initialize
kmp_file = KMPFile(LDAttr.discover())

# Load existing mapping
mapping = kmp_file.getCustomize("shooter")

# Modify settings
mapping.configInfo.resolutionPattern.width = 1920
mapping.configInfo.resolutionPattern.height = 1080
mapping.keyboardConfig.mouseCenter = Point(x=960, y=540)

# Update first key position
if mapping.keyboardMappings:
    mapping.keyboardMappings[0].data.point.x = 150
    mapping.keyboardMappings[0].data.point.y = 150

# Save modified version
kmp_file.dump("shooter_modified.kmp", mapping)
print("Mapping saved!")
```
