from abc import ABC, abstractmethod
from typing import override

import pyautogui as gui

from .region import Region, RegionSpec
from .utils import locate_on_screen


class ReferenceElement(ABC):
    """Base class for reference elements used to identify scenes."""

    @abstractmethod
    def locate(self, region: RegionSpec | None = None) -> Region | None:
        """Detect the presence of the reference element."""
        raise NotImplementedError("Subclasses must implement this method")

    def locate_and_click(
        self, offset: tuple[int, int] = (0, 0), clicks: int = 1, button: str = "left"
    ):
        """Locate the reference element and click on it."""
        region = self.locate()
        assert region is not None, f"Element {self} not found on screen"
        # TODO: unify moving logic with utils
        gui.moveTo(
            region.center[0] + offset[0],
            region.center[1] + offset[1],
            0.6,
            gui.easeInOutQuad,  # type: ignore
        )
        gui.click(clicks=clicks, button=button)
        return True


class ImageElement(ReferenceElement):
    """Reference element that identifies a scene by an image."""

    def __init__(
        self,
        path: str | list[str],
        confidence: float = 0.999,
        region: RegionSpec | None = None,
    ):
        self.path = path
        self.confidence = confidence
        self.region = region

    @override
    def locate(self, region: RegionSpec | None = None):
        """Method to detect the presence of the image in the current screen."""
        if isinstance(self.path, str):
            path = [self.path]  # Ensure path is a list for consistency
        else:
            path = self.path
        for image_path in path:
            try:
                location = locate_on_screen(
                    image_path, region=region or self.region, confidence=self.confidence
                )
                return location
            except gui.ImageNotFoundException:
                continue


class TextElement(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(
        self,
        text: str,
        region: RegionSpec | None = None,
        case_sensitive: bool = False,
    ):
        self.text = text
        self.region = region
        self.case_sensitive = case_sensitive
        if not case_sensitive:
            self.text = self.text.lower()

    def locate(self, region: RegionSpec | None = None):
        """Method to detect the presence of the text in the current screen."""
        from .ocr import OCR

        ocr = OCR()
        region = region or self.region
        for text, detected_region in ocr.recognize_text(
            gui.screenshot(region=Region.from_spec(region).to_box() if region else None)
        ):
            if not self.case_sensitive:
                text = text.lower()
            if text.strip() == self.text.strip():
                return detected_region
        return None
