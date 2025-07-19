import pyautogui as gui

from pyautoscene import ImageElement, Scene, Session, TextElement

# Define all elements separately
add_to_cart = ImageElement("examples/saucedemo/references/add_to_cart_button.png")
username = ImageElement("examples/saucedemo/references/username.png")
backpack = TextElement(
    "Sauce Labs Bike Light", region="x:2/2 y:(2-4)/5", case_sensitive=False
)
cart_icon = ImageElement("examples/saucedemo/references/cart_icon.png")
checkout_button = ImageElement("examples/saucedemo/references/checkout_button.png")

login = Scene(
    "Login",
    elements=[
        TextElement("Username", region="x:2/3 y:(1-2)/3"),
        TextElement("Password", region="x:2/3 y:(1-2)/3"),
        # ReferenceImage("examples/saucedemo/references/login_button.png"),
    ],
    initial=True,
)

dashboard = Scene(
    "Dashboard",
    elements=[
        TextElement("Swag Labs", region="x:2/3 y:1/3"),
        TextElement("Products", region="x:1/3 y:1/3"),
    ],
)

cart = Scene(
    "Cart", elements=[TextElement("Your Cart", region="x:1/3 y:1/3"), cart_icon]
)


@login.action(transitions_to=dashboard)
def perform_login(username_inp: str, password_inp: str):
    """Performs the login action to transition from Login to Dashboard."""
    username.locate_and_click()
    gui.write(username_inp, interval=0.1)
    gui.press("tab")
    gui.write(password_inp, interval=0.1)
    gui.press("enter")


@dashboard.action()
def add_products_to_cart(target: str):
    """Adds products to the cart."""
    if target == "backpack":
        backpack.locate_and_click()
    else:
        backpack.locate_and_click()
    add_to_cart.locate_and_click(region="x:2/3 y:(2-3)/3", clicks=1)


@dashboard.action(transitions_to=cart)
def view_cart():
    """Views the cart."""
    cart_icon.locate_and_click()


@cart.action()
def checkout():
    """Checks out the items in the cart."""
    checkout_button.locate_and_click()


session = Session(scenes=[login, dashboard, cart])

gui.hotkey("alt", "tab")
session.expect(dashboard, username_inp="standard_user", password_inp="secret_sauce")
session.invoke("add_products_to_cart", target="backpack")
session.invoke("view_cart")
session.invoke("checkout")
