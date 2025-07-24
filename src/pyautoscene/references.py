from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, override

import pyautogui as gui
import pyscreeze
from PIL import Image

from ._types import Direction, MouseButton
from .actions import locate_on_screen, move_and_click
from .region import Region, RegionSpec
from .utils import get_file


class ReferenceElement(ABC):
    """Base class for reference elements used to identify scenes."""

    name: str

    @abstractmethod
    def locate(
        self, region: RegionSpec | None = None, n: int = 1
    ) -> list[Region] | None:
        """Detect the presence of the reference element."""
        raise NotImplementedError("Subclasses must implement this method")

    def locate_and_click(
        self,
        offset: int = 0,
        region: RegionSpec | None = None,
        clicks: int = 1,
        button: MouseButton = "left",
        towards: Direction | None = None,
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
        self.name = Path(path).stem if isinstance(path, str) else Path(path[0]).stem

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
            except (gui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                continue

        return all_locations if all_locations else None

    def __repr__(self) -> str:
        return f"ImageElement: {self.path}"


class ReferenceImageDir:
    def __init__(self, dir_path: Path | str) -> None:
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        assert dir_path.is_dir(), f"{dir_path} is not a valid directory."
        self.dir_path = dir_path
        self.images: dict[str, ImageElement] = {}

    def __call__(
        self,
        image_name: str,
        region: RegionSpec | None = None,
        confidence: float = 0.999,
        locator: Callable[[Image.Image, Image.Image], list[Region]] | None = None,
    ) -> ImageElement:
        """Get an ImageElement from the reference directory."""
        if image_name not in self.images:
            image_path = get_file(self.dir_path, name=image_name)
            self.images[image_name] = ImageElement(
                str(image_path), region=region, confidence=confidence, locator=locator
            )
        return self.images[image_name]


def image(
    path: str,
    region: RegionSpec | None = None,
    confidence: float = 0.999,
    locator: Callable[[Image.Image, Image.Image], list[Region]] | None = None,
) -> ImageElement:
    """Create an image reference element."""
    return ImageElement(path, confidence=confidence, region=region, locator=locator)


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
        self.name = text

    def locate(
        self, region: RegionSpec | None = None, n: int = 1
    ) -> list[Region] | None:
        """Method to detect the presence of the text in the current screen."""
        from .ocr import OCR

        ocr = OCR()
        region = region or self.region
        found_regions = []

        for text, detected_region in ocr.recognize_text(
            gui.screenshot(
                region=Region.from_spec(region).to_tuple() if region else None
            )
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

    def __repr__(self) -> str:
        return f"{{TextElement: {self.text}}}"


def text(
    text: str,
    region: RegionSpec | None = None,
    case_sensitive: bool = False,
    full_text: bool = False,
) -> TextElement:
    """Create a text reference element."""
    return TextElement(
        text=text, region=region, case_sensitive=case_sensitive, full_text=full_text
    )
