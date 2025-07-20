from __future__ import annotations

import logging
from keyword import iskeyword
from pathlib import Path
from typing import Literal

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

    for path in dir.glob(name):
        if path.suffix in valid_extensions:
            return path
    raise FileNotFoundError(f"File {name} not found in directory {dir}")
