from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pyautogui as gui
from pyscreeze import Box

type RegionSpec = Region | str

axis_pattern = re.compile(r"(?P<d>[xy]):\(?(?P<i>\d+)(?:-(?P<j>\d+))?\)?/(?P<n>\d+)")


@dataclass(frozen=True, slots=True)
class Region:
    left: int
    top: int
    width: int
    height: int

    def to_box(self) -> Box:
        """Convert to a pyscreeze Box."""
        return Box(self.left, self.top, self.width, self.height)

    @classmethod
    def from_box(cls, box: Box) -> Region:
        """Create a Region from a pyscreeze Box."""
        return cls(left=box.left, top=box.top, width=box.width, height=box.height)

    @property
    def center(self) -> tuple[int, int]:
        """Get the center coordinates of the region."""
        return (self.left + self.width // 2, self.top + self.height // 2)

    @classmethod
    def from_spec(
        cls, spec: RegionSpec, shape: tuple[int, int] | None = None
    ) -> Region:
        if isinstance(spec, Region):
            return spec
        if shape is None:
            img = np.array(gui.screenshot())
            shape = (img.shape[0]), (img.shape[1])

        default_region = {"left": 0, "top": 0, "width": shape[1], "height": shape[0]}

        axis_mapping = {"x": ("left", "width", 1), "y": ("top", "height", 0)}
        for axis, i, j, n in axis_pattern.findall(spec):
            alignment, size_attr, dim_index = axis_mapping[axis]
            size = shape[dim_index] // int(n)
            i, j = int(i), int(j) if j else int(i)
            default_region.update({
                alignment: (i - 1) * size,
                size_attr: (j - i + 1) * size,
            })

        return cls(**default_region)

    def resolve(self, base: RegionSpec | None) -> Region:
        if base is None:
            return self
        if isinstance(base, str):
            base = Region.from_spec(base)
        return Region(
            left=self.left + base.left,
            top=self.top + base.top,
            width=self.width,
            height=self.height,
        )
