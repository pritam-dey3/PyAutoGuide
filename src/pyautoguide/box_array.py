from __future__ import annotations

import warnings
from collections.abc import Iterable, Sequence
from typing import Callable

from ._types import Direction
from .shapes import Box, BoxSpec
from .utils import line_intersects_box


class BoxArray(Sequence[Box]):
    """An immutable sequence of Box objects that proxies methods to its contents."""

    def __init__(self, boxes: Iterable[Box] | None = None) -> None:
        self._boxes = tuple(boxes) if boxes is not None else ()

    def __getitem__(self, index: int | slice) -> Box | BoxArray:
        """Returns a Box or a new BoxArray from a slice."""
        if isinstance(index, slice):
            return BoxArray(self._boxes[index])
        return self._boxes[index]

    def __len__(self) -> int:
        """Returns the number of boxes in the array."""
        return len(self._boxes)

    def __add__(self, boxes: object) -> BoxArray:
        """Extends the BoxArray with additional Box objects."""
        if not isinstance(boxes, Iterable):
            raise TypeError(f"Expected an iterable of Box objects, got {type(boxes)}")
        new_boxes = tuple(boxes)
        if not all(isinstance(box, Box) for box in new_boxes):
            raise TypeError("All items must be instances of Box.")
        return BoxArray(new_boxes + self._boxes)

    def first(self) -> Box:
        """Returns the first Box in the array."""
        if not self._boxes:
            raise IndexError("BoxArray is empty.")
        return self._boxes[0]

    def last(self) -> Box:
        """Returns the last Box in the array."""
        if not self._boxes:
            raise IndexError("BoxArray is empty.")
        return self._boxes[-1]

    def select(self, *, i: int) -> Box:
        """Returns the Box at the specified index."""
        return self._boxes[i]

    def pick(self, region: BoxSpec) -> BoxArray:
        """Returns a new BoxArray with boxes those have center inside the region."""

        new_boxes = [box for box in self._boxes if box.center in Box.from_spec(region)]
        return BoxArray(new_boxes)

    def filter_by(self, condition: Callable[[Box], bool]) -> BoxArray:
        """Returns a new BoxArray with boxes that satisfy the given condition."""
        new_boxes = [box for box in self._boxes if condition(box)]
        return BoxArray(new_boxes)

    def relative_to(self, direction: Direction, *, of: BoxSpec) -> BoxArray:
        """Returns a new BoxArray with boxes relative to the specified direction and origin."""
        if isinstance(of, str):
            of = Box.from_spec(of)
        return BoxArray(
            (
                box
                for box in self._boxes
                if line_intersects_box(box, direction, of.center)
            )
        )

    def __getattr__(self, name: str):
        """Dynamically proxies method calls to the specified Box."""
        # Check if the attribute is a callable method on the Box class
        if not hasattr(Box, name) or not callable(getattr(Box, name)):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        def method_proxy(*args, **kwargs):
            """Proxy function that calls the method on the selected Box."""
            if not self._boxes:
                raise ValueError(f"BoxArray is empty, cannot call method {name}.")

            new_boxes = []
            for box in self._boxes:
                try:
                    return_value = getattr(box, name)(*args, **kwargs)
                    if isinstance(return_value, Box):
                        new_boxes.append(return_value)
                    elif isinstance(return_value, BoxArray):
                        new_boxes.extend(return_value._boxes)
                    else:
                        raise TypeError(
                            f"Method {name} returned unexpected type: {type(return_value)}"
                        )
                except Exception as e:
                    warnings.warn(
                        f"Method {name} raised an exception: {e}", stacklevel=2
                    )
            return BoxArray(new_boxes)

        return method_proxy
