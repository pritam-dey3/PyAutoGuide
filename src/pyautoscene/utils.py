from __future__ import annotations
import time
from typing import Literal
import pyautogui as gui

LOCATE_AND_CLICK_DELAY = 0.2

def locate_and_click(
    filename: str, clicks: int = 1, button: Literal["left", "right"] = "left"
):
    time.sleep(LOCATE_AND_CLICK_DELAY)
    locate = gui.locateOnScreen(filename, grayscale=True)
    assert locate is not None, f"Could not locate {filename} on screen."
    locate_center = (locate.left + locate.width // 2), (locate.top + locate.height // 2)
    gui.moveTo(*locate_center, 0.6, gui.easeInOutQuad)  # type: ignore
    gui.click(clicks=clicks, button=button)
    time.sleep(LOCATE_AND_CLICK_DELAY)