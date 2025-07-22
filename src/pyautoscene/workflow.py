import logging
import time
from random import random
from typing import Callable

import networkx as nx
import pyautogui as gui
from transitions.extensions import GraphMachine

from .references import ReferenceElement
from .utils import get_nx_graph

logger = logging.getLogger(__name__)


class NavigationError(Exception):
    """Custom exception for navigation errors."""

    pass


class WorkFlow:
    """Manages transitions and actions without explicit scenes."""

    def __init__(self, name: str):
        self.name = name
        self.elements: dict[str, ReferenceElement] = {}
        self.navigations: dict[str, Callable] = {}
        self.actions: dict[str, Callable] = {}
        self._sm = GraphMachine()

    def add_element(self, element: ReferenceElement):
        """Add a reference element to the workflow."""
        if element.name not in self.elements:
            self.elements[element.name] = element
            self._sm.add_state(element.name)

    def navigation(self, source: ReferenceElement, to: ReferenceElement):
        """Decorator to define transitions between UI states."""
        self.add_element(source)
        self.add_element(to)

        def decorator[T: Callable](func: T) -> T:
            transition_name = "event_" + func.__name__
            self._sm.add_transition(transition_name, source.name, to.name, prepare=func)
            self.navigations[transition_name] = func
            return func

        return decorator

    def action(self, name: str | None = None):
        """Decorator to define actions that don't change UI state."""

        def decorator[T: Callable](func: T) -> T:
            action_name = name or func.__name__
            self.actions[f"action_{action_name}"] = func
            return func

        return decorator

    def invoke(self, name: str, **kwargs):
        """Execute an action or transition."""
        if (aname := f"action_{name}") in self.actions:
            return self.actions[aname](**kwargs)
        elif (nname := f"event_{name}") in self.navigations:
            return self.navigations[nname](**kwargs)
        raise ValueError(f"Action or navigation '{name}' not found.")

    def get_visible_elements(self) -> list[ReferenceElement]:
        """Return a list of currently visible elements in the workflow."""
        return [elem for elem in self.elements.values() if elem.locate(n=1) is not None]

    def expect(self, elem: ReferenceElement, **kwargs):
        """Navigate to a specific scene."""
        if elem.locate(n=1) is not None:
            return

        graph = get_nx_graph(self._sm)

        visible_elements = self.get_visible_elements()
        all_paths = []
        for present_elem in visible_elements:
            all_paths.extend(
                nx.all_simple_paths(graph, source=present_elem.name, target=elem.name)
            )
        if len(all_paths) == 0:
            raise NavigationError(f"No path found from {present_elem} to {elem}")
        elif len(all_paths) > 1:
            raise NavigationError(f"Multiple paths found from {present_elem} to {elem}")

        path = all_paths[0]
        events: list[str] = [
            graph.get_edge_data(path[i], path[i + 1])[0]["label"]  # type: ignore
            for i in range(len(path) - 1)
        ]
        logger.info(events)

        old_state = self._sm.state
        try:
            self._sm.set_state(path[0])
            for event in events:
                self._sm.dispatch(event, **kwargs)
        except Exception as e:
            self._sm.set_state(old_state)
            raise e

    def wait_for(
        self,
        element: ReferenceElement | list[ReferenceElement],
        timeout: float = 60,
        interval: float = 1,
        keep_busy: bool = True,
    ):
        """Wait until the target scene or reference element is on screen."""
        found = False
        while not found:
            if isinstance(element, ReferenceElement):
                found = element.locate(n=1) is not None
            elif isinstance(element, list):
                for elem in element:
                    assert isinstance(elem, ReferenceElement), (
                        "All elements in the list must be ReferenceElement instances."
                    )
                found = any(elem.locate(n=1) is not None for elem in element)
            else:
                raise TypeError("Target must be a ReferenceElement.")
            start_time = time.time()
            if not found:
                if time.time() - start_time > timeout:
                    raise NavigationError(f"Timeout waiting for {element}")
                w, h = gui.size()
                if keep_busy:
                    gui.moveTo(
                        w * random(),
                        h * random(),
                        duration=2 * interval * random(),
                        tween=gui.easeInOutQuad,  # type: ignore
                    )
                time.sleep(interval)
