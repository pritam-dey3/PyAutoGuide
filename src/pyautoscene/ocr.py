import logging
import os
from hashlib import sha256
from pathlib import Path

import numpy as np
from PIL import Image

from .shapes import Box

logger = logging.getLogger(__name__)

try:
    from rapidocr import RapidOCR
    from rapidocr.utils.output import RapidOCROutput
except ImportError:
    raise ImportError(
        "RapidOCR is not installed. Please install it using 'pip install pyautoscene[ocr]'."
    )

default_ocr_config_path = Path(__file__).parent / "ocr_config.yaml"
ocr_config_path = Path(os.getenv("PYAUTOSCENE_OCR_CONFIG", default_ocr_config_path))
logger.info(f"OCR config path: {ocr_config_path}")


def hash_image(img: Image.Image) -> str:
    return sha256(img.tobytes()).hexdigest()


def convert_points_to_ltwh(points: np.ndarray) -> Box:
    if points.shape[0] == 0:
        raise ValueError("Points array is empty")

    x_min = int(np.min(points[:, 0]))
    y_min = int(np.min(points[:, 1]))
    x_max = int(np.max(points[:, 0]))
    y_max = int(np.max(points[:, 1]))

    return Box(left=x_min, top=y_min, width=x_max - x_min, height=y_max - y_min)


class OCR:
    engine: RapidOCR | None = None
    img_cache: dict[str, tuple[tuple[str, Box], ...]] = {}

    def __new__(cls):
        if cls.engine is None:
            cls.engine = RapidOCR(config_path=ocr_config_path.as_posix())
        return super().__new__(cls)

    def recognize_text(self, img: Image.Image) -> tuple[tuple[str, Box], ...]:
        img_gray = img.convert("L")
        img_hash = hash_image(img_gray)
        if img_hash in self.img_cache:
            logger.debug(f"Using cached result for image hash: {img_hash}")
            return self.img_cache[img_hash]

        assert self.engine is not None, "Engine should be initialized in __new__"
        result = self.engine(np.array(img_gray))
        assert isinstance(result, RapidOCROutput), (
            "Result should be of type RapidOCROutput"
        )
        assert result.txts is not None and result.boxes is not None, (
            "Text recognition failed, txts and boxes should not be None"
        )

        detections = tuple(
            (txt, convert_points_to_ltwh(box))
            for txt, box in zip(result.txts, result.boxes)
        )
        self.img_cache[img_hash] = detections
        return detections
