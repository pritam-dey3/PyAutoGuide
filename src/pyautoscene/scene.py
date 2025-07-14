from __future__ import annotations

from typing import Callable, TypedDict

from statemachine import State

from pyautoscene.utils import is_valid_variable_name

from .references import ReferenceElement
from .screen import Region


class ActionInfo(TypedDict):
    """Type definition for action information in a scene."""

    action: Callable[..., None]
    transitions_to: Scene | None


class Scene(State):
    """A scene represents a state in the GUI automation state machine."""

    def __init__(
        self,
        name: str,
        elements: list[ReferenceElement] | None = None,
        initial: bool = False,
    ):
        assert is_valid_variable_name(name), (
            f"Invalid scene name: {name}, must be a valid Python identifier."
        )
        super().__init__(name, initial=initial)
        self.elements = elements or []
        self.actions: dict[str, ActionInfo] = {}

    def action(self, transitions_to: Scene | None = None):
        """Decorator to register an action for this scene."""

        def decorator(func: Callable[..., None]) -> Callable[..., None]:
            if func.__name__ not in self.actions:
                action_name = func.__name__
                self.actions[action_name] = {
                    "action": func,
                    "transitions_to": transitions_to,
                }
            return func

        return decorator

    def get_action(self, action_name: str) -> ActionInfo | None:
        """Get an action by name."""
        return self.actions.get(action_name)

    def is_on_screen(self, region: Region | None = None) -> bool:
        """Check if any reference element is currently on screen."""
        # TODO: Refactor after text recognition is implemented
        # elements = (elem for elem in self.elements if isinstance(elem, ReferenceImage))
        return all(elem.is_visible(region) for elem in self.elements)

    def __repr__(self):
        return f"Scene({self.name!r}, elements={len(self.elements)})"
