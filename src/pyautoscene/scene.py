from __future__ import annotations

from typing import Callable

from statemachine import State

from pyautoscene.utils import is_valid_variable_name

from .references import ReferenceElement


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
        self._actions = {}

    def action(self, transitions_to: Scene | None = None):
        """Decorator to register an action for this scene."""

        def decorator(func: Callable[..., None]) -> Callable[..., None]:
            if func.__name__ not in self._actions:
                action_name = func.__name__
                self._actions[action_name] = {
                    "action": func,
                    "transitions_to": transitions_to,
                }
            return func

        return decorator

    def get_action(self, action_name: str) -> dict | None:
        """Get an action by name."""
        return self._actions.get(action_name)

    def get_actions(self) -> dict:
        """Get all actions for this scene."""
        return self._actions.copy()

    def __repr__(self):
        return f"Scene({self.name!r}, elements={len(self.elements)})"
