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

    def __init__(self, image_path: str):
        self.image_path = image_path

    def is_visible(self, region: Box | None = None):
        """Method to detect the presence of the image in the current screen."""
        try:
            return gui.locateOnScreen(self.image_path, region=region)
        except gui.ImageNotFoundException:
            return None


class ReferenceText(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(self, text: str):
        self.text = text

    def is_visible(self):
        """Method to detect the presence of the text in the current screen."""
        raise NotImplementedError("Text recognition is not implemented yet.")
