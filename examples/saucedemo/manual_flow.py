import pyautogui as gui

from pyautoscene import ImageElement, Scene, Session, TextElement
from pyautoscene.utils import locate_and_click

login = Scene(
    "Login",
    elements=[
        TextElement("Welcome to Login"),
        ImageElement("examples/saucedemo/references/login_button.png"),
    ],
    initial=True,
)

dashboard = Scene(
    "Dashboard",
    elements=[
        TextElement("Swag Labs"),
        TextElement("Products"),
        ImageElement("examples/saucedemo/references/cart_icon.png"),
    ],
)

cart = Scene(
    "Cart",
    elements=[
        TextElement("Your Cart"),
        ImageElement("examples/saucedemo/references/cart_icon.png"),
    ],
)


@login.action(transitions_to=dashboard)
def perform_login(username: str, password: str):
    """Performs the login action to transition from Login to Dashboard."""
    locate_and_click("examples/saucedemo/references/username.png")
    gui.write(username, interval=0.1)
    gui.press("tab")
    gui.write(password, interval=0.1)
    gui.press("enter")


@dashboard.action()
def add_products_to_cart(target: str):
    """Adds products to the cart."""
    locate_and_click(f"examples/saucedemo/references/{target}.png")
    locate_and_click("examples/saucedemo/references/add_to_cart_button.png")


@dashboard.action(transitions_to=cart)
def view_cart():
    """Views the cart."""
    locate_and_click("examples/saucedemo/references/cart_icon.png")


@cart.action()
def checkout():
    """Checks out the items in the cart."""
    locate_and_click("examples/saucedemo/references/checkout_button.png")


session = Session(scenes=[login, dashboard, cart])

# test internal state machine
gui.hotkey("alt", "tab")
print(f"{session.current_scene=}")
session.invoke("perform_login", username="standard_user", password="secret_sauce")
print(f"After login: {session._sm.current_state=}")
session.invoke("add_products_to_cart", target="backpack")
session.invoke("view_cart")
print(f"After adding to cart: {session._sm.current_state=}")
session.invoke("checkout")
