from __future__ import annotations

from typing import Callable

from statemachine import State, StateMachine
from statemachine.factory import StateMachineMetaclass
from statemachine.states import States
from statemachine.transition_list import TransitionList

from .scene import Scene


def build_dynamic_state_machine(
    scenes: list[Scene],
) -> tuple[StateMachine, dict[str, TransitionList], dict[str, Callable]]:
    """Create a dynamic StateMachine class from scenes using StateMachineMetaclass."""

    states = {scene.name: scene for scene in scenes}
    transitions = {}
    leaf_actions = {}
    for scene in scenes:
        for action_name, action_info in scene.actions.items():
            target_scene = action_info["transitions_to"]
            if target_scene is not None:
                event_name = f"event_{action_name}"
                new_transition = scene.to(target_scene, event=event_name)
                new_transition.on(action_info["action"])
                transitions[event_name] = new_transition
            else:
                leaf_actions[action_name] = action_info["action"]

    SessionSM = StateMachineMetaclass(
        "SessionSM",
        (StateMachine,),
        {"states": States(states), **transitions},  # type: ignore[call-arg]
    )
    session_sm: StateMachine = SessionSM()  # type: ignore[no-redef]

    return session_sm, transitions, leaf_actions


class Session:
    """A session manages the state machine for GUI automation scenes."""

    def __init__(self, scenes: list[Scene]):
        self._scenes_list = scenes
        self._scenes_dict = {scene.name: scene for scene in scenes}

        # Create dynamic StateMachine class and instantiate it
        self._sm, self.transitions, self.leaf_actions = build_dynamic_state_machine(
            scenes
        )

    @property
    def current_scene(self) -> State:
        """Get the current state."""
        return self._sm.current_state

    def goto(self, target_scene):
        """Navigate to a specific scene."""
        if target_scene is None:
            raise ValueError("Cannot navigate to None scene")

        if isinstance(target_scene, Scene):
            scene_name = target_scene.name
        else:
            scene_name = str(target_scene)

        if scene_name not in self._scenes_dict:
            raise ValueError(f"Scene '{scene_name}' not found in session")

        # Find the corresponding state in the state machine
        target_state = None
        for state in self._sm.states:
            if state.name == scene_name:
                target_state = state
                break

        if target_state:
            # Force the current state - this works with the new implementation
            self._sm.current_state = target_state
        else:
            raise ValueError(f"Could not find state for scene '{scene_name}'")

    def invoke(self, action_name: str, **kwargs):
        """Invoke an action in the current scene."""
        event_name = f"event_{action_name}"
        transition = next(
            (tr for tr_name, tr in self.transitions.items() if tr_name == event_name),
            None,
        )
        if transition:
            return self._sm.send(event_name, **kwargs)

        leaf_action = next(
            (
                action
                for name, action in self.leaf_actions.items()
                if name == action_name
            ),
            None,
        )
        if leaf_action:
            return leaf_action(**kwargs)

        raise ValueError(
            f"Action '{action_name}' not found in current scene '{self.current_scene.name}'"
        )

    def __repr__(self):
        current = self.current_scene
        current_name = current.name if current else "None"
        return (
            f"Session(scenes={list(self._scenes_dict.keys())}, current={current_name})"
        )
