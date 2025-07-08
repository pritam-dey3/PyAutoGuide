from typing import Any


class ReferenceElement:
    """Base class for reference elements used to identify scenes."""

    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"


class ReferenceImage(ReferenceElement):
    """Reference element that identifies a scene by an image."""

    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.image_path = image_path


class ReferenceText(ReferenceElement):
    """Reference element that identifies a scene by text."""

    def __init__(self, text: str):
        super().__init__(text)
        self.text = text
