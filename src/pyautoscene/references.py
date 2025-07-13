from abc import ABC, abstractmethod

import pyautogui as gui
from pyscreeze import Box


class ReferenceElement(ABC):
    """Base class for reference elements used to identify scenes."""

    @abstractmethod
    def is_visible(self):
        """Detect the presence of the reference element."""
        raise NotImplementedError("Subclasses must implement this method")


class ReferenceImage(ReferenceElement):
    """Reference element that identifies a scene by an image."""

    def __init__(
        self,
        path: str | list[str],
        confidence: float = 0.999,
        region: Box | None = None,
    ):
        self.path = path
        self.confidence = confidence
        self.region = region

    def is_visible(self, region: Box | None = None):
        """Method to detect the presence of the image in the current screen."""
        if isinstance(self.path, str):
            path = [self.path]  # Ensure path is a list for consistency
        else:
            path = self.path
        for image_path in path:
            try:
                location = gui.locateOnScreen(
                    image_path, region=region or self.region, confidence=self.confidence
                )
                return location
            except gui.ImageNotFoundException:
                continue


class ReferenceText(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(self, text: str):
        self.text = text

    def is_visible(self):
        """Method to detect the presence of the text in the current screen."""
        raise NotImplementedError("Text recognition is not implemented yet.")
