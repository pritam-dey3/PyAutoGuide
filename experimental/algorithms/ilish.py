from typing import Literal

import cv2
import numpy as np
from PIL import Image

from pyautoscene.shapes import Box

type OpenCvTransformKernel = Literal["CROSS", "RECT", "ELLIPSE"]
type OpenCvTransformMorphology = Literal[
    "ERODE", "DILATE", "OPEN", "CLOSE", "GRADIENT", "TOPHAT", "BLACKHAT", "HITMISS"
]
type OpenCvThresholdAlgo = Literal[
    "BINARY",
    "BINARY_INV",
    "TRUNC",
    "TOZERO",
    "TOZERO_INV",
    "MASK",
    "OTSU",
    "TRIANGLE",
    "DRYRUN",
]
type OpenCvMatchAlgo = Literal[
    "SQDIFF", "SQDIFF_NORMED", "CCORR", "CCORR_NORMED", "CCOEFF", "CCOEFF_NORMED"
]


def ilish(
    needle: Image.Image,
    haystack: Image.Image,
    *,
    transform_kernel: OpenCvTransformKernel = "ELLIPSE",
    transform_shape: tuple[int, int] = (53, 53),
    transform_morphology: OpenCvTransformMorphology = "BLACKHAT",
    threshold: int = 127,
    threshold_max_value: int = 255,
    threshold_algo: OpenCvThresholdAlgo = "BINARY_INV",
    match_algo: OpenCvMatchAlgo = "SQDIFF",
    match_mask_value: int | None = 255,
    confidence: float = 0.9,
):
    def transform(inp: Image.Image) -> np.ndarray:
        gray = cv2.cvtColor(np.array(inp.convert("RGB")), cv2.COLOR_RGB2GRAY)
        kernel = cv2.getStructuringElement(
            getattr(cv2, f"MORPH_{transform_kernel}"), transform_shape
        )
        blackhat = cv2.morphologyEx(
            gray, getattr(cv2, f"MORPH_{transform_morphology}"), kernel
        )
        thresh = cv2.threshold(
            blackhat,
            threshold,
            threshold_max_value,
            getattr(cv2, f"THRESH_{threshold_algo}"),
        )[1]
        return thresh

    if haystack.size[0] < needle.size[0] or haystack.size[1] < needle.size[1]:
        raise ValueError(
            "needle dimension(s) exceed the haystack image or region dimensions"
        )

    needle_t = transform(needle)
    haystack_t = transform(haystack)
    result = cv2.matchTemplate(
        haystack_t,
        needle_t,
        getattr(cv2, f"TM_{match_algo}"),
        None,
        (needle_t != match_mask_value).astype(np.uint8)
        if match_mask_value is not None
        else None,
    )

    if match_algo.startswith("SQDIFF"):
        match_filter = result < confidence
    else:
        match_filter = result > confidence

    match_indices = np.arange(result.size)[match_filter.flatten()]
    matches = np.unravel_index(match_indices, result.shape)

    match_regions = [
        Box(x, y, needle.width, needle.height) for x, y in zip(matches[1], matches[0])
    ]
    return (match_regions, result, needle_t, haystack_t)
