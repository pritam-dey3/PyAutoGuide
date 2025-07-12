import pyautogui as gui

from pyautoscene import ReferenceImage, ReferenceText, Scene, Session
from pyautoscene.utils import locate_and_click

# 1. Define Scenes: Create scenes with their identifying elements
login = Scene(
    "Login",
    elements=[
        ReferenceText("Welcome to Login"),
        ReferenceImage("references/login_button.png"),
    ],
)

dashboard = Scene(
    "Dashboard",
    elements=[
        ReferenceText("Swag Labs"),
        ReferenceText("Products"),
        ReferenceImage("references/cart_icon.png"),
    ],
)

cart = Scene(
    "Cart",
    elements=[ReferenceText("Your Cart"), ReferenceImage("references/cart_icon.png")],
)

# 2. Define Actions: Use the new @scene.action decorator.
#    The decorated function will contain the pyautogui logic for the action.
#    The function's name implicitly becomes the action's name.


@login.action(transitions_to=dashboard)
def perform_login(username: str, password: str):
    """Performs the login action to transition from Login to Dashboard."""
    locate_and_click("references/username.png")
    gui.write(username, interval=0.1)
    gui.press("tab")
    gui.write(password, interval=0.1)
    gui.press("enter")


@dashboard.action()
def add_products_to_cart(target: str):
    """Adds products to the cart."""
    locate_and_click(f"references/{target}.png")
    locate_and_click("references/add_to_cart_button.png")


@dashboard.action(transitions_to=cart)
def view_cart():
    """Views the cart."""
    locate_and_click("references/cart_icon.png")


@cart.action()
def checkout():
    """Checks out the items in the cart."""
    locate_and_click("references/checkout_button.png")


# 3. Example usage patterns that could be supported:
session = Session(scenes=[login, dashboard, cart])
session.goto(dashboard)
session.invoke("add_products_to_cart", target="backpack")
session.invoke("view_cart")
session.invoke("checkout")
