from pathlib import Path

import pyautogui as gui

from pyautoscene import ReferenceImageDir, WorkFlow, text

# Initialize reference directory
refs = ReferenceImageDir(Path("examples/saucedemo/references"))

# Create workflow
wf = WorkFlow("SauceDemo")


@wf.navigation(
    text("Username", region="x:2/3 y:(1-2)/3"), text("Products", region="x:1/3 y:1/3")
)
def perform_login(username: str, password: str):
    """Performs the login action to transition from Login to Dashboard."""
    # refs("username").locate().click()
    refs("username").locate().click()
    gui.write(username, interval=0.1)
    gui.press("tab")
    gui.write(password, interval=0.1)
    # text("Swag Labs").locate_and_click(index=1, offset=400, towards="bottom")
    text("Swag Labs").locate(n=2).select(i=1).offset("bottom", 400).click()


@wf.action()
def add_products_to_cart(target: str):
    """Adds products to the cart."""
    if target == "backpack":
        text(
            "Sauce Labs Bike Light", region="x:2/2 y:(2-4)/5", case_sensitive=False
        ).locate().click()
    else:
        text(
            "Sauce Labs Bike Light", region="x:2/2 y:(2-4)/5", case_sensitive=False
        ).locate().click()
    refs("add_to_cart_button").locate(region="x:2/3 y:(2-3)/3").click(clicks=1)


@wf.navigation(
    text("Swag Labs", region="x:2/3 y:1/3"), text("Your Cart", region="x:1/3 y:1/3")
)
def view_cart():
    """Views the cart."""
    # refs("cart_icon").locate().click()
    text("Remove", region="x:2/3 y:3/3").locate().first().find_color(
        color=(226, 35, 26), towards="top-right", region="x:5/5 y:1/4"
    ).click()


@wf.action()
def checkout():
    """Checks out the items in the cart."""
    refs("checkout_button").locate().click()


gui.hotkey("alt", "tab")
wf.expect(
    text("Products", region="x:1/3 y:1/3"),
    username="standard_user",
    password="secret_sauce",
)
wf.invoke("add_products_to_cart", target="backpack")
wf.expect(text("Your Cart", region="x:1/3 y:1/3"))
wf.invoke("checkout")
