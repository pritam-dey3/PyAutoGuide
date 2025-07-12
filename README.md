# PyAutoScene

**Advanced GUI Automation with Scene-Based State Management**

PyAutoScene is a Python library that provides a declarative approach to GUI automation by modeling application interfaces as scenes and transitions. It combines element detection with state machine patterns to create robust, maintainable automation scripts.

## 🌟 Features

- **Scene-Based Architecture**: Model your application as a collection of scenes with defined elements and transitions
- **Visual Element Detection**: Supports both image-based element recognition. (Text recognition support coming soon!)
- **Automatic Navigation**: Intelligent pathfinding between scenes using graph algorithms
- **Action Decorators**: Clean, declarative syntax for defining scene actions and transitions

## 🚀 Quick Start

### Installation

```bash
pip install pyautoscene
```

### Basic Example

Here's how to automate a simple login flow:

```python
import pyautogui as gui
from pyautoscene import ReferenceImage, ReferenceText, Scene, Session
from pyautoscene.utils import locate_and_click

# Define scenes
login = Scene(
    "Login",
    elements=[
        ReferenceText("Welcome to Login"),
        ReferenceImage("references/login_button.png"),
    ],
    initial=True,
)

dashboard = Scene(
    "Dashboard",
    elements=[
        ReferenceText("Dashboard"),
        ReferenceImage("references/user_menu.png"),
    ],
)

# Define actions with transitions
@login.action(transitions_to=dashboard)
def perform_login(username: str, password: str):
    """Performs login and transitions to dashboard."""
    locate_and_click("references/username_field.png")
    gui.write(username, interval=0.1)
    gui.press("tab")
    gui.write(password, interval=0.1)
    gui.press("enter")

# Create session and navigate
session = Session(scenes=[login, dashboard])
session.expect(dashboard, username="user", password="pass")
```

## 📖 Core Concepts

### Scenes

A **Scene** represents a distinct state in your application's UI. Each scene contains:

- **Elements**: Visual markers that identify when the scene is active
- **Actions**: Functions that can be performed in this scene
- **Transitions**: Connections to other scenes

```python
scene = Scene(
    "SceneName",
    elements=[
        ReferenceImage("path/to/image.png"),
        ReferenceText("Expected Text"),
    ],
    initial=False  # Set to True for starting scene
)
```

### Reference Elements

PyAutoScene supports two types of reference elements:

#### ReferenceImage

Detects scenes using image matching:

```python
ReferenceImage("path/to/reference/image.png")
```

#### ReferenceText
(Coming soon)
Detects scenes using text recognition:

```python
ReferenceText("Expected text on screen")
```

### Actions and Transitions

Actions are decorated functions that define what can be done in a scene:

```python
@scene.action(transitions_to=target_scene)  # Action that changes scenes
def action_with_transition():
    # Perform GUI operations
    pass

@scene.action()  # Action that stays in current scene
def action_without_transition():
    # Perform GUI operations
    pass
```

### Session Management

The **Session** class manages the state machine and provides navigation:

```python
session = Session(scenes=[scene1, scene2, scene3])

# Navigate to a specific scene (finds optimal path)
session.expect(target_scene, **action_params)

# Invoke an action in the current scene
session.invoke("action_name", **action_params)

# Get current scene
current = session.current_scene
```

### Automatic Scene Detection

PyAutoScene automatically detects which scene is currently active:

```python
from pyautoscene.session import get_current_scene

current_scene = get_current_scene(scenes)
print(f"Currently on: {current_scene.name}")
```

### Path Finding

The library uses NetworkX to find optimal paths between scenes:

```python
# This will automatically navigate: Login → Dashboard → Cart
session.expect(cart_scene, username="user", password="pass")
```

### Error Handling

```python
from pyautoscene.session import SceneRecognitionError

try:
    session.expect(target_scene)
except SceneRecognitionError as e:
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

- [ ] Text recognition implementation
- [ ] Enhanced image matching algorithms
- [ ] Multiple session support

