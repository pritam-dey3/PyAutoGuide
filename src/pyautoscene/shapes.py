from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pyautogui as gui
from pyscreeze import Box as BoxTuple

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
    def center(self) -> tuple[int, int]:
        """Get the center coordinates of the box."""
        return (self.left + self.width // 2, self.top + self.height // 2)

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

    def click(
        self,
        clicks: int = 1,
        button: MouseButton = "left",
        offset: int = 0,
        towards: Direction | None = None,
        base: BoxSpec | None = None,
    ):
        """Click at the center of the box with optional offset."""
        from .actions import move_and_click

        target_box = self.resolve(base)
        move_and_click(
            target_box=target_box,
            clicks=clicks,
            button=button,
            offset=offset,
            towards=towards,
        )


BoxSpec = Box | str
