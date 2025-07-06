import pyautogui as gui
from pyautoscene.utils import locate_and_click

gui.hotkey('alt', 'tab')
locate_and_click("references/username.png")
gui.write("standard_user", interval=0.1)
gui.press("tab")
gui.write("secret_sauce", interval=0.1)
gui.press("enter") 