from abc import ABC, abstractmethod
from typing import Callable, override

import pyautogui as gui
from PIL import Image

from ._types import MouseButton, TowardsDirection
from .region import Region, RegionSpec
from .utils import locate_on_screen, move_and_click


class ReferenceElement(ABC):
    """Base class for reference elements used to identify scenes."""

    @abstractmethod
    def locate(
        self, region: RegionSpec | None = None, n: int = 1
    ) -> list[Region] | None:
        """Detect the presence of the reference element."""
        raise NotImplementedError("Subclasses must implement this method")

    def locate_and_click(
        self,
        offset: tuple[int, int] = (0, 0),
        region: RegionSpec | None = None,
        clicks: int = 1,
        button: MouseButton = "left",
        towards: TowardsDirection = None,
        index: int = 0,
    ):
        """Locate the reference element and click on it."""
        regions = self.locate(region=region, n=index + 1)
        assert regions is not None and len(regions) > index, (
            f"Element {self} not found on screen or insufficient detections {len(regions) if regions else 0} < {index + 1}."
        )
        move_and_click(
            target_region=regions[index],
            clicks=clicks,
            button=button,
            offset=offset,
            towards=towards,
        )


class ImageElement(ReferenceElement):
    """Reference element that identifies a scene by an image."""

    def __init__(
        self,
        path: str | list[str],
        confidence: float = 0.999,
        region: RegionSpec | None = None,
        locator: Callable[[Image.Image, Image.Image], list[Region]] | None = None,
    ):
        self.path = path
        self.confidence = confidence
        self.region = region
        self.locator = locator

    @override
    def locate(
        self, region: RegionSpec | None = None, n: int = 1
    ) -> list[Region] | None:
        """Method to detect the presence of the image in the current screen."""
        if isinstance(self.path, str):
            path = [self.path]  # Ensure path is a list for consistency
        else:
            path = self.path

        all_locations: list[Region] = []
        for image_path in path:
            try:
                locations = locate_on_screen(
                    image_path,
                    region=region if region else self.region,
                    confidence=self.confidence,
                    locator=self.locator,
                    limit=n - len(all_locations),  # Only get remaining needed locations
                )
                if locations is not None:
                    all_locations.extend(locations)

                # If we have enough detections, return them
                if len(all_locations) >= n:
                    return all_locations[:n]
            except gui.ImageNotFoundException:
                continue

        return all_locations if all_locations else None


class TextElement(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(
        self,
        text: str,
        region: RegionSpec | None = None,
        case_sensitive: bool = False,
        full_text: bool = False,
    ):
        self.text = text
        self.region = region
        self.case_sensitive = case_sensitive
        self.full_text = full_text
        if not case_sensitive:
            self.text = self.text.lower()

    def locate(
        self, region: RegionSpec | None = None, n: int = 1
    ) -> list[Region] | None:
        """Method to detect the presence of the text in the current screen."""
        from .ocr import OCR

        ocr = OCR()
        region = region or self.region
        found_regions = []

        for text, detected_region in ocr.recognize_text(
            gui.screenshot(region=Region.from_spec(region).to_box() if region else None)
        ):
            if not self.case_sensitive:
                text = text.lower()
            if self.full_text and text.strip() == self.text.strip():
                found_regions.append(detected_region.resolve(base=region))
            elif not self.full_text and self.text in text:
                found_regions.append(detected_region.resolve(base=region))
            # If we have enough detections, return them
            if len(found_regions) >= n:
                return found_regions[:n]

        return found_regions if found_regions else None
