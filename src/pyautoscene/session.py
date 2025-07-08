from __future__ import annotations

from statemachine import State, StateMachine
from statemachine.factory import StateMachineMetaclass

from .scene import Scene


def create_session_class(scenes: list[Scene]) -> type[StateMachine]:
    """Create a dynamic StateMachine class from scenes using StateMachineMetaclass."""

    # Create states definition
    states_definition = {}
    for i, scene in enumerate(scenes):
        state_name = scene.name.lower().replace(" ", "_").replace("-", "_")
        states_definition[state_name] = {
            "initial": i == 0,  # First scene is initial
            "final": False,
        }

    # Create states instances
    states_instances = {
        state_id: State(scenes[i].name, **state_kwargs)
        for i, (state_id, state_kwargs) in enumerate(states_definition.items())
    }

    # Create events (transitions) based on scene actions
    events = {}
    for scene in scenes:
        for action_name, action_info in scene.get_actions().items():
            if action_info["transitions_to"] is not None:
                source_scene = scene
                target_scene = action_info["transitions_to"]

                # Find the corresponding state instances
                source_state_name = (
                    source_scene.name.lower().replace(" ", "_").replace("-", "_")
                )
                target_state_name = (
                    target_scene.name.lower().replace(" ", "_").replace("-", "_")
                )

                source_state = states_instances[source_state_name]
                target_state = states_instances[target_state_name]

                # Create transition
                transition = source_state.to(target_state, event=action_name)

                if action_name in events:
                    events[action_name] |= transition
                else:
                    events[action_name] = transition

    # Combine states and events for the metaclass
    attrs_mapper = {**states_instances, **events}

    # Create the StateMachine class using the metaclass
    return StateMachineMetaclass("DynamicSession", (StateMachine,), attrs_mapper)  # type: ignore[return-value]


class Session:
    """A session manages the state machine for GUI automation scenes."""

    def __init__(self, scenes: list[Scene]):
        self._scenes_list = scenes
        self._scenes_dict = {scene.name: scene for scene in scenes}

        # Create dynamic StateMachine class and instantiate it
        SessionClass = create_session_class(scenes)
        self._state_machine = SessionClass()

    @property
    def current_state(self) -> State:
        """Get the current state."""
        return self._state_machine.current_state

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
        for state in self._state_machine.states:
            if state.name == scene_name:
                target_state = state
                break

        if target_state:
            # Force the current state - this works with the new implementation
            self._state_machine.current_state = target_state
        else:
            raise ValueError(f"Could not find state for scene '{scene_name}'")

    def invoke(self, action_name: str, **kwargs):
        """Invoke an action in the current scene."""
        current_state = self.current_state
        current_scene_name = current_state.name
        current_scene = self._scenes_dict[current_scene_name]

        action_info = current_scene.get_action(action_name)

        if action_info is None:
            raise ValueError(
                f"Action '{action_name}' not found in current scene '{current_scene_name}'"
            )

        # Execute the action function
        action_function = action_info["function"]
        result = action_function(**kwargs)

        # Handle transition if specified using the state machine's event system
        if action_info["transitions_to"] is not None:
            # Try to use the state machine's transition if it exists
            if hasattr(self._state_machine, action_name):
                # Use the state machine's transition method
                getattr(self._state_machine, action_name)()
            else:
                # Fallback to manual transition
                target_scene = action_info["transitions_to"]
                if target_scene is not None:
                    self.goto(target_scene)

        return result

    def get_current_scene(self) -> Scene:
        """Get the current scene."""
        current_state_name = self.current_state.name
        return self._scenes_dict[current_state_name]

    def __repr__(self):
        current = self.get_current_scene()
        current_name = current.name if current else "None"
        return (
            f"Session(scenes={list(self._scenes_dict.keys())}, current={current_name})"
        )
