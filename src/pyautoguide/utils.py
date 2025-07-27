from __future__ import annotations

import logging
from keyword import iskeyword
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import networkx as nx
import numpy as np
import pydot
from transitions.extensions import GraphMachine

if TYPE_CHECKING:
    from .shapes import Box, Point

from ._types import Direction

logger = logging.getLogger(__name__)


def is_valid_variable_name(name: str) -> bool:
    return name.isidentifier() and not iskeyword(name)


def get_file(
    dir: Path, *, name: str, file_type: Literal["image", "text"] = "image"
) -> Path:
    """Find a file in the given directory."""
    image_file_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
    text_file_extensions = [".txt", ".md", ".json"]

    if file_type == "image":
        valid_extensions = image_file_extensions
    elif file_type == "text":
        valid_extensions = text_file_extensions
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    for path in dir.glob(f"{name}.*"):
        if path.suffix in valid_extensions:
            return path
    raise FileNotFoundError(f"File {name} not found in directory {dir}")


def get_nx_graph(machine: GraphMachine) -> nx.MultiDiGraph:
    pydot_graph = pydot.graph_from_dot_data(machine.get_graph().source)[0]  # type: ignore
    nx_graph = nx.nx_pydot.from_pydot(pydot_graph)
    return nx_graph


def direction_to_vector(direction: Direction) -> np.ndarray:
    mapping = {
        "right": 0,
        "top": 90,
        "left": 180,
        "bottom": 270,
        "top-left": 135,
        "top-right": 45,
        "bottom-left": 225,
        "bottom-right": 315,
    }
    deg = mapping[direction] if isinstance(direction, str) else direction
    rad = np.deg2rad(deg)
    return np.array([np.cos(rad), -np.sin(rad)])


def line_intersects_box(
    box: Box, direction: Direction, point: Point
) -> tuple[Point, ...]:
    """Check if a box intersects with a line in a specific direction."""
    d = direction_to_vector(direction)
    sides = [
        ((box.left, box.top), (0, -1), box.height),  # left side
        ((box.left, box.top + box.height), (1, 0), box.width),  # bottom side
        (
            (box.left + box.width, box.top + box.height),
            (0, 1),
            box.height,
        ),  # right side
        ((box.left + box.width, box.top), (-1, 0), box.width),  # top side
    ]
    intersections = ()
    for corner, line_dir, length in sides:
        line_start = np.array(corner)
        line_dir_ = np.array(line_dir)
        try:
            t, u = np.linalg.solve(np.array([line_dir_, -d]).T, point - line_start)
        except np.linalg.LinAlgError:
            continue
        if 0 <= t <= length and u >= 0:
            intersections += (point + (u * d),)
    return intersections


def get_search_region_in_direction(
    box: Box, towards: Direction, size: tuple[int, int]
) -> Box:
    """Get the search region in a specific direction from the given box."""
    from .shapes import Box

    if towards == "top-right":
        return Box(
            left=box.left + box.width,
            top=0,
            width=size[0] - (box.left + box.width),
            height=box.top,
        )
    elif towards == "top-left":
        return Box(left=0, top=0, width=box.left, height=box.top)
    elif towards == "bottom-right":
        return Box(
            left=box.left + box.width,
            top=box.top + box.height,
            width=size[0] - (box.left + box.width),
            height=size[1] - (box.top + box.height),
        )
    elif towards == "bottom-left":
        return Box(
            left=0,
            top=box.top + box.height,
            width=box.left + box.width,
            height=size[1] - (box.top + box.height),
        )
    elif towards == "top":
        return Box(left=box.left, top=0, width=box.width, height=box.top)
    elif towards == "bottom":
        return Box(
            left=box.left,
            top=box.top + box.height,
            width=box.width,
            height=size[1] - (box.top + box.height),
        )
    elif towards == "left":
        return Box(left=0, top=box.top, width=box.left, height=box.height)
    elif towards == "right":
        return Box(
            left=box.left + box.width,
            top=box.top,
            width=size[0] - (box.left + box.width),
            height=box.height,
        )
    else:
        raise ValueError(f"Unknown direction: {towards}")


# def generate_points(
#     source: Point, towards: Direction, offset: int = 0, max_distance: int = 10_000_000
# ):
#     step = direction_to_vector(towards)
#     i = offset
#     while True:
#         yield Point(*np.round(source + step * i))
#         i += 1
#         if i > max_distance:
#             break
