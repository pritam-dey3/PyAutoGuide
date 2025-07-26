from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

import numpy as np
import pyautogui as gui
from pyscreeze import Box as BoxTuple

from pyautoscene.utils import direction_to_vector

from ._types import Direction, MouseButton

axis_pattern = re.compile(r"(?P<d>[xy]):\(?(?P<i>\d+)(?:-(?P<j>\d+))?\)?/(?P<n>\d+)")


@dataclass(frozen=True, slots=True)
class Box:
    left: int
    top: int
    width: int
    height: int

    def to_tuple(self) -> BoxTuple:
        """Convert to a pyscreeze Box."""
        return BoxTuple(self.left, self.top, self.width, self.height)

    @classmethod
    def from_tuple(cls, box: BoxTuple) -> Box:
        """Create a Region from a pyscreeze Box."""
        return cls(left=box.left, top=box.top, width=box.width, height=box.height)

    @property
    def center(self) -> Point:
        """Get the center coordinates of the box."""
        return Point(x=self.left + self.width // 2, y=self.top + self.height // 2)

    @classmethod
    def from_spec(cls, spec: BoxSpec, shape: tuple[int, int] | None = None) -> Box:
        if isinstance(spec, Box):
            return spec
        if shape is None:
            img = np.array(gui.screenshot())
            shape = (img.shape[0]), (img.shape[1])

        default_box = {"left": 0, "top": 0, "width": shape[1], "height": shape[0]}

        axis_mapping = {"x": ("left", "width", 1), "y": ("top", "height", 0)}
        for axis, i, j, n in axis_pattern.findall(spec):
            alignment, size_attr, dim_index = axis_mapping[axis]
            size = shape[dim_index] // int(n)
            i, j = int(i), int(j) if j else int(i)
            default_box.update({
                alignment: (i - 1) * size,
                size_attr: (j - i + 1) * size,
            })

        return cls(**default_box)

    def resolve(self, base: BoxSpec | None) -> Box:
        if base is None:
            return self
        if isinstance(base, str):
            base = Box.from_spec(base)
        return Box(
            left=self.left + base.left,
            top=self.top + base.top,
            width=self.width,
            height=self.height,
        )

    def click(self, clicks: int = 1, button: MouseButton = "left") -> Self:
        """Click at the center of the box with optional offset."""
        from .actions import move_and_click

        move_and_click(target=self, clicks=clicks, button=button)
        return self

    def offset(self, direction: Direction, offset: int = 0) -> Box:
        """Return a new Box offset in the specified direction."""
        vector = direction_to_vector(direction)
        return Box(
            left=self.left + vector[0] * offset,
            top=self.top + vector[1] * offset,
            width=self.width,
            height=self.height,
        )

    def __contains__(self, point: Point) -> bool:
        """Check if a Point is inside the Box."""
        return (
            self.left <= point.x <= self.left + self.width
            and self.top <= point.y <= self.top + self.height
        )


type BoxSpec = Box | str


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int

    def to_tuple(self) -> tuple[int, int]:
        """Convert to a tuple."""
        return (self.x, self.y)

    def __add__(self, other: Point | np.ndarray) -> Point:
        """Add another Point or a numpy array to this Point."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, np.ndarray):
            return Point(self.x + int(other[0]), self.y + int(other[1]))
        raise TypeError("Unsupported type for addition with Point.")

    def __radd__(self, other: Point | np.ndarray) -> Point:
        """Add this Point to another Point or a numpy array."""
        return self.__add__(other)

    def __iter__(self):
        """Return an iterator over the Point coordinates."""
        yield self.x
        yield self.y

    @classmethod
    def from_tuple(cls, point: tuple[int, int]) -> Point:
        """Create a Point from a tuple."""
        return cls(x=point[0], y=point[1])

    def __array__(self, dtype=None, copy=None):
        return np.array([self.x, self.y], dtype=dtype, copy=copy)

    def resolve(self, base: Point | None) -> Point:
        """Return a new Point offset by another Point (base)."""
        if base is None:
            return self
        if isinstance(base, tuple):
            base = Point.from_tuple(base)
        return Point(self.x + base.x, self.y + base.y)

    def offset(self, direction: Direction, offset: int = 0) -> Point:
        """Return a new Point offset in the specified direction."""
        vector = direction_to_vector(direction)
        return self + vector * offset

    def click(self, clicks: int = 1, button: MouseButton = "left"):
        """Click at the Point location."""

        from pyautoscene.actions import move_and_click

        move_and_click(target=self, clicks=clicks, button=button)
        return self
