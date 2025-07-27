from __future__ import annotations

from typing import Literal

type MouseButton = Literal["left", "right"]
type Direction = (
    Literal[
        "top",
        "left",
        "bottom",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]
    | int
)
