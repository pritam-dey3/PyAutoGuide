import logging
import os
import time
from typing import Callable

import numpy as np
import pyautogui as gui
from PIL import Image

from ._types import Direction, MouseButton
from .constants import LOCATE_AND_CLICK_DELAY, POINTER_SPEED
from .shapes import Box, BoxSpec
from .utils import direction_to_vector

logger = logging.getLogger(__name__)


def locate_and_click(
    reference: Image.Image | str,
    clicks: int = 1,
    button: MouseButton = "left",
    region: BoxSpec | None = None,
    confidence: float = 0.999,
    grayscale: bool = True,
    offset: int = 0,
    towards: Direction | None = None,
    index: int = 0,
):
    time.sleep(LOCATE_AND_CLICK_DELAY)
    found_region = locate_on_screen(
        reference,
        region=region,
        confidence=confidence,
        grayscale=grayscale,
        limit=index + 1,
    )
    assert found_region is not None, f"Could not locate {reference} on screen."
    assert len(found_region) > index, (
        f"Not enough detections for {reference}: {len(found_region)}"
    )
    move_and_click(
        found_region[index],
        clicks=clicks,
        button=button,
        offset=offset,
        towards=towards,
    )
    time.sleep(LOCATE_AND_CLICK_DELAY)


def move_and_click(
    target_box: BoxSpec,
    clicks: int = 1,
    button: MouseButton = "left",
    offset: int = 0,
    towards: Direction | None = None,
):
    """Move to the center or edge of the region and click.

    The offset is always added to the calculated target point.
    For example, for 'bottom', offset=(0, 5) means 5 pixels below the bottom edge.
    """
    direction = direction_to_vector(towards) if towards else np.array([0, 0])
    target = np.array(target_box.center) + offset * direction

    current = gui.position()
    duration = np.linalg.norm(np.array(target) - np.array(current)) / POINTER_SPEED
    gui.moveTo(*target, float(duration), gui.easeInOutQuad)  # type: ignore
    gui.click(clicks=clicks, button=button)


def locate_on_screen(
    reference: Image.Image | str,
    region: BoxSpec | None = None,
    confidence: float = 0.999,
    grayscale: bool = True,
    limit: int = 1,
    locator: Callable[[Image.Image, Image.Image], list[Box]] | None = None,
) -> list[Box] | None:
    """Locate a region on the screen."""
    if isinstance(reference, str):
        if not os.path.exists(reference):
            raise FileNotFoundError(f"Image file {reference} does not exist.")
        reference = Image.open(reference)
    if locator is None:
        try:
            locations = list(
                gui.locateAllOnScreen(
                    reference,
                    region=Box.from_spec(region).to_tuple() if region else None,
                    grayscale=grayscale,
                    confidence=confidence,
                )
            )
            return [Box.from_tuple(loc) for loc in locations[:limit]]
        except gui.ImageNotFoundException:
            return None
        except FileNotFoundError:
            return None
    else:
        screenshot = gui.screenshot(
            region=Box.from_spec(region).to_tuple() if region else None
        )
        logger.info(
            f"Searching in region: {Box.from_spec(region).to_tuple() if region else None}.\nGiven region: {region}"
        )
        detections = locator(reference, screenshot)
        logger.info("total detections: %d", len(detections))
        if len(detections) == 0:
            return None
        else:
            return [det.resolve(region) for det in detections[:limit]]
