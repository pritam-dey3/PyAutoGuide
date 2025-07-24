from __future__ import annotations

import logging
from keyword import iskeyword
from pathlib import Path
from typing import Literal

import networkx as nx
import numpy as np
import pydot
from transitions.extensions import GraphMachine

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
    mapping = {"right": 0, "top": 90, "left": 180, "bottom": 270}
    deg = mapping[direction] if isinstance(direction, str) else direction
    rad = np.deg2rad(deg)
    return np.array([np.cos(rad), -np.sin(rad)])
