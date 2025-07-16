from __future__ import annotations

import time
from keyword import iskeyword
from typing import Literal

import pyautogui as gui
from PIL import Image

from .region import Region, RegionSpec

LOCATE_AND_CLICK_DELAY = 0.2


def locate_and_click(
    filename: str, clicks: int = 1, button: Literal["left", "right"] = "left"
):
    time.sleep(LOCATE_AND_CLICK_DELAY)
    locate = gui.locateOnScreen(filename, grayscale=True)
    assert locate is not None, f"Could not locate {filename} on screen."
    locate_center = (locate.left + locate.width // 2), (locate.top + locate.height // 2)
    # TODO: don't hardcode duration. should be ideally distance / speed
    gui.moveTo(*locate_center, 0.6, gui.easeInOutQuad)  # type: ignore
    gui.click(clicks=clicks, button=button)
    time.sleep(LOCATE_AND_CLICK_DELAY)


def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)


def locate_on_screen(
    reference: Image.Image | str,
    region: RegionSpec | None = None,
    confidence: float = 0.999,
    grayscale: bool = True,
    limit: int = 1,
) -> Region | None:
    """Locate a region on the screen."""
    try:
        location = gui.locateOnScreen(
            reference,
            region=Region.from_spec(region).to_box() if region else None,
            grayscale=grayscale,
            confidence=confidence,
            limit=limit,
        )
        if location:
            return Region.from_box(location)
    except gui.ImageNotFoundException:
        return None
    except FileNotFoundError:
        return None
