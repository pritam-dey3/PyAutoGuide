import logging
import os
import time
from typing import Callable

import numpy as np
import pyautogui as gui
from PIL import Image

from ._types import MouseButton, TowardsDirection
from .constants import LOCATE_AND_CLICK_DELAY, POINTER_SPEED
from .region import Region, RegionSpec

logger = logging.getLogger(__name__)


def locate_and_click(
    reference: Image.Image | str,
    clicks: int = 1,
    button: MouseButton = "left",
    region: RegionSpec | None = None,
    confidence: float = 0.999,
    grayscale: bool = True,
    offset: tuple[int, int] = (0, 0),
    towards: TowardsDirection | None = None,
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
    target_region: RegionSpec,
    clicks: int = 1,
    button: MouseButton = "left",
    offset: tuple[int, int] = (0, 0),
    towards: TowardsDirection | None = None,
):
    """Move to the center or edge of the region and click.

    The offset is always added to the calculated target point.
    For example, for 'bottom', offset=(0, 5) means 5 pixels below the bottom edge.
    """
    _target_region = Region.from_spec(target_region)
    base_points = {
        "top": (_target_region.center[0], _target_region.top),
        "left": (_target_region.left, _target_region.center[1]),
        "bottom": (
            _target_region.center[0],
            _target_region.top + _target_region.height - 1,
        ),
        "right": (
            _target_region.left + _target_region.width - 1,
            _target_region.center[1],
        ),
        None: _target_region.center,
    }
    if towards not in base_points:
        raise ValueError(f"Invalid direction: {towards}")
    base = base_points[towards]
    target = (base[0] + offset[0], base[1] + offset[1])

    current = gui.position()
    duration = np.linalg.norm(np.array(target) - np.array(current)) / POINTER_SPEED
    gui.moveTo(*target, float(duration), gui.easeInOutQuad)  # type: ignore
    gui.click(clicks=clicks, button=button)


def locate_on_screen(
    reference: Image.Image | str,
    region: RegionSpec | None = None,
    confidence: float = 0.999,
    grayscale: bool = True,
    limit: int = 1,
    locator: Callable[[Image.Image, Image.Image], list[Region]] | None = None,
) -> list[Region] | None:
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
                    region=Region.from_spec(region).to_tuple() if region else None,
                    grayscale=grayscale,
                    confidence=confidence,
                )
            )
            return [Region.from_tuple(loc) for loc in locations[:limit]]
        except gui.ImageNotFoundException:
            return None
        except FileNotFoundError:
            return None
    else:
        screenshot = gui.screenshot(
            region=Region.from_spec(region).to_tuple() if region else None
        )
        logger.info(
            f"Searching in region: {Region.from_spec(region).to_tuple() if region else None}.\nGiven region: {region}"
        )
        detections = locator(reference, screenshot)
        logger.info("total detections: %d", len(detections))
        if len(detections) == 0:
            return None
        else:
            return [det.resolve(region) for det in detections[:limit]]
