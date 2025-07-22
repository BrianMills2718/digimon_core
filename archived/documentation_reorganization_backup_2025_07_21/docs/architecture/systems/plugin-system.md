---
status: living
---

# KGAS Plugin System

## Overview
The KGAS Plugin System allows users and third parties to extend the system with new tools and phases without modifying the core codebase. Plugins are loaded dynamically via setuptools entry points.

## Plugin Contract
- Must implement a `run(self, *args, **kwargs)` method (for ToolPlugin)
- Must be discoverable via the `kgas.plugins` entry point
- Should follow the interface documented in this file

## Loading Flowchart
```
[KGAS Startup]
      |
      v
[Discover setuptools entry points: kgas.plugins]
      |
      v
[Import plugin classes]
      |
      v
[Register ToolPlugin/PhasePlugin]
      |
      v
[Available for use in workflows]
```

## Hello-World Plugin Tutorial

### 1. Create your plugin file (my_plugin.py):
```python
class MyToolPlugin:
    def run(self, *args, **kwargs):
        print('Hello from MyToolPlugin!')
```

### 2. Add setup.py:
```python
from setuptools import setup
setup(
    name='my_kgas_plugin',
    version='0.1',
    py_modules=['my_plugin'],
    entry_points={
        'kgas.plugins': [
            'my_tool = my_plugin:MyToolPlugin',
        ],
    },
)
```

### 3. Install your plugin:
```bash
pip install -e .
```

### 4. KGAS will auto-discover and load your plugin at startup.

---
For advanced plugin interfaces and lifecycle hooks, see the developer guide. 