# PyAutoGuide

**Advanced GUI Automation with Workflow-Based State Management**

PyAutoGuide is a Python library that provides a declarative approach to GUI automation by modeling application workflows as state transitions between UI elements. It combines advanced element detection with state machine patterns to create robust, maintainable automation scripts.

## 🌟 Features

- **Workflow-Based Architecture**: Model your application as workflows with state transitions between UI elements
- **Advanced Visual Element Detection**: Supports both image-based and text-based element recognition with sophisticated matching
- **Flexible Region Specification**: Mathematical region syntax for targeting specific screen areas with precision
- **Automatic Navigation**: Intelligent pathfinding between UI states using graph algorithms
- **Action & Navigation Decorators**: Clean, declarative syntax for defining workflows and state transitions
- **Reference Image Management**: Directory-based image reference system for organized asset management
- **Object-Oriented Element Operations**: Fluent API with method chaining for complex element interactions
- **Color-Based Detection**: Advanced color finding capabilities with directional search
- **Multiple Result Handling**: Sophisticated selection strategies for multiple matching elements
- **Integration Ready**: Seamless integration with PyAutoGUI and other automation tools

## 🚀 Quick Start

### Installation

```bash
pip install pyautoguide
```

### Basic Example

Here's how to automate a simple login flow using the new workflow-based approach:

```python
from pathlib import Path
import pyautogui as gui
from pyautoguide import ReferenceImageDir, WorkFlow, text

# Initialize reference directory for organized image management
refs = ReferenceImageDir(Path("references"))

# Create workflow
workflow = WorkFlow("LoginFlow")

# Define navigation between UI states
@workflow.navigation(
    text("Username", region="x:2/3 y:(1-2)/3"),  # Source state
    text("Dashboard", region="x:1/3 y:1/3")      # Target state
)
def perform_login(username: str, password: str):
    """Performs login and transitions to dashboard."""
    refs("username_field").locate().click()
    gui.write(username, interval=0.1)
    gui.press("tab")
    gui.write(password, interval=0.1)
    gui.press("enter")

# Define an action that doesn't change state
@workflow.action()
def add_item_to_cart(item_name: str):
    """Adds an item to cart without changing UI state."""
    text(item_name, case_sensitive=False).locate().click()
    refs("add_to_cart_button").locate(region="x:2/3 y:(2-3)/3").click()

# Execute workflow with automatic navigation
workflow.expect(
    text("Dashboard", region="x:1/3 y:1/3"),
    username="user",
    password="pass"
)

# Invoke actions directly
workflow.invoke("add_item_to_cart", item_name="Product Name")
```

## 📖 Core Concepts

### WorkFlows

A **WorkFlow** represents the automation logic for your application. Unlike the deprecated Scene-based approach, workflows focus on element transitions and actions:

```python
from pyautoguide import WorkFlow

workflow = WorkFlow("MyApp")
```

### Reference Elements & Image Management

PyAutoGuide provides sophisticated element detection and management:

#### ReferenceImageDir

Organize your reference images in directories:

```python
from pathlib import Path
from pyautoguide import ReferenceImageDir

refs = ReferenceImageDir(Path("references"))
# Use as: refs("button_name").locate().click()
```

#### Direct Element Creation

Create elements directly for text and images:

```python
from pyautoguide import text, image

# Text elements with advanced options
text_elem = text("Expected Text", case_sensitive=False)

# Image elements
image_elem = image("path/to/image.png")
```

### Advanced Region Specification

PyAutoGuide supports sophisticated region syntax with mathematical expressions:

```python
# Search in top-left third
text("Login", region="x:1/3 y:1/3")

# Search in middle horizontal band
text("Welcome", region="y:2/3")

# Search spanning multiple columns/rows
text("Header", region="x:(1-2)/3 y:1/3")

# Complex mathematical expressions
text("Content", region="x:(2-4)/5 y:(1-2)/3")
```

### Object-Oriented Element Operations

PyAutoGuide provides a fluent API for complex element interactions:

```python
# Multiple result handling
text("Button").locate(n=2).select(i=1).click()

# Directional operations
element.locate().offset("bottom", 400).click()

# Color-based detection
element.locate().find_color(
    color=(226, 35, 26),
    towards="top-right",
    region="x:5/5 y:1/4"
).click()

# Chained operations
text("Item").locate().first().offset("right", 50).click()
```

### Navigation and Actions

The workflow system uses decorators to define state transitions and actions:

#### Navigation Decorators

Define transitions between UI states:

```python
@workflow.navigation(source_element, target_element)
def transition_function(**params):
    # Perform GUI operations that lead to state change
    pass
```

#### Action Decorators

Define actions that don't change UI state:

```python
@workflow.action()
def action_function(**params):
    # Perform GUI operations without state change
    pass
```

### WorkFlow Execution

Execute workflows with intelligent navigation:

```python
# Navigate to specific UI state (finds optimal path automatically)
workflow.expect(target_element, **action_params)

# Invoke specific actions
workflow.invoke("action_name", **action_params)

# Wait for elements to appear
workflow.wait_for(element, timeout=60, interval=1)
```

### Element Detection

PyAutoGuide automatically detects visible elements and manages workflow state:

```python
# Get currently visible elements
visible_elements = workflow.get_visible_elements()

# Check if element is currently visible
is_visible = element.locate(n=1, error="coerce") is not None
```

### Advanced Path Finding

The library uses NetworkX for optimal path finding between UI states:

```python
# Automatically navigates through intermediate states
workflow.expect(final_state, **params)
```

### Error Handling

```python
from pyautoguide.workflow import NavigationError

try:
    workflow.expect(target_element)
except NavigationError as e:
    print(f"Navigation failed: {e}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run pre-commit hooks: `pre-commit run --all-files`
5. Submit a pull request

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

- [x] Spatial relationship modeling between elements
- [ ] Multiple workflow support
- [ ] Advanced debugging and visualization tools

## 🙏 Credits

PyAutoGuide builds on the work of several open-source projects:

- [PyAutoGUI](https://github.com/asweigart/pyautogui) by Al Sweigart
- [python-statemachine](https://github.com/fgmacedo/python-statemachine) by Filipe Macedo
- [RapidOCR](https://github.com/RapidAI/RapidOCR) by RapidAI contributors
