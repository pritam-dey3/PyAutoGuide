from __future__ import annotations

from typing import Callable

import networkx as nx
from statemachine import State, StateMachine
from statemachine.factory import StateMachineMetaclass
from statemachine.states import States
from statemachine.transition_list import TransitionList

from .scene import Scene
from .screen import Region


class SceneRecognitionError(Exception):
    pass


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


def get_current_scene(scenes: list[Scene], region: Region | None = None) -> Scene:
    """Get the current scene from the list of scenes."""
    current_scenes = [scene for scene in scenes if scene.is_on_screen(region)]
    if len(current_scenes) == 1:
        return current_scenes[0]
    elif len(current_scenes) > 1:
        raise SceneRecognitionError(
            f"Multiple scenes are currently on screen.\n{' '.join(str(scene) for scene in current_scenes)}"
        )
    else:
        raise SceneRecognitionError("No scene is currently on screen.")


class Session:
    """A session manages the state machine for GUI automation scenes."""

    def __init__(self, scenes: list[Scene]):
        self._scenes_list = scenes
        self._scenes_dict = {scene.name: scene for scene in scenes}

        # Create dynamic StateMachine class and instantiate it
        self._sm, self.transitions, self.leaf_actions = build_dynamic_state_machine(
            scenes
        )
        self.graph: nx.MultiDiGraph = nx.nx_pydot.from_pydot(self._sm._graph())

    @property
    def current_scene(self) -> State:
        """Get the current state."""
        return self._sm.current_state

    def expect(self, target_scene: Scene, **kwargs):
        """Navigate to a specific scene."""
        if target_scene.is_on_screen():
            return

        present_scene = get_current_scene(self._scenes_list)
        all_paths = list(
            nx.all_simple_paths(
                self.graph,
                source=present_scene.name,
                target=target_scene.name,
            )
        )
        if len(all_paths) == 0:
            raise SceneRecognitionError(
                f"No path found from {present_scene.name} to {target_scene.name}"
            )
        elif len(all_paths) > 1:
            raise SceneRecognitionError(
                f"Multiple paths found from {present_scene.name} to {target_scene.name}"
            )

        path = all_paths[0]
        events: list[str] = [
            self.graph.get_edge_data(path[i], path[i + 1])[0]["label"]  # type: ignore
            for i in range(len(path) - 1)
        ]

        for event in events:
            self._sm.send(event, **kwargs)

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
