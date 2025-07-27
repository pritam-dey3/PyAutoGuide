from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import cv2
import numpy as np
import pyautogui as gui
from pyscreeze import Box as BoxTuple

from pyautoscene.utils import direction_to_vector, get_search_region_in_direction

from ._types import Direction, MouseButton

if TYPE_CHECKING:
    from .box_array import BoxArray

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

    def offset(self, direction: Direction, shift: int = 0) -> Box:
        """Return a new Box offset in the specified direction."""
        vector = direction_to_vector(direction)
        return Box(
            left=self.left + vector[0] * shift,
            top=self.top + vector[1] * shift,
            width=self.width,
            height=self.height,
        )

    def __contains__(self, point: Point) -> bool:
        """Check if a Point is inside the Box."""
        return (
            self.left <= point.x <= self.left + self.width
            and self.top <= point.y <= self.top + self.height
        )

    def intersect(self, other: Box) -> Box:
        """Return the intersection of two Boxes."""
        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.left + self.width, other.left + other.width)
        bottom = min(self.top + self.height, other.top + other.height)

        if left < right and top < bottom:
            return Box(left=left, top=top, width=right - left, height=bottom - top)
        raise ValueError("Boxes do not intersect.")

    def find_color(
        self,
        color: tuple[int, int, int],
        towards: Direction,
        *,
        region: BoxSpec | None = None,
    ) -> BoxArray:
        """Find the median pixel with given color in the direction."""
        from .box_array import BoxArray

        # Determine search region based on direction
        assert isinstance(towards, str), "integer direction is not supported"
        search_region = get_search_region_in_direction(self, towards, size=gui.size())

        # Apply optional region constraint
        if region:
            given_region = Box.from_spec(region)
            search_region = search_region.intersect(given_region)

        # Take screenshot of search region
        img = gui.screenshot(region=search_region.to_tuple())

        # Find connected components of the target color
        color_array = np.array(color)
        img_color_mask = np.all(np.array(img) == color_array, axis=-1).astype(np.uint8)
        n, img_label = cv2.connectedComponents(
            img_color_mask, connectivity=8, ltype=cv2.CV_32S
        )

        # Find all bounding boxes of connected components
        det_boxes = []
        for i in range(1, n):
            mask = img_label == i
            coords = np.column_stack(np.where(mask))
            if coords.size == 0:
                continue
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            # Convert to absolute coordinates
            det_boxes.append(
                Box(
                    left=x_min,
                    top=y_min,
                    width=x_max - x_min + 1,
                    height=y_max - y_min + 1,
                )
            )

        if not det_boxes:
            raise ValueError(
                f"No pixels with color {color} found in direction {towards}"
            )

        return BoxArray([b.resolve(search_region) for b in det_boxes])


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

        from .actions import move_and_click

        move_and_click(target=self, clicks=clicks, button=button)
        return self
