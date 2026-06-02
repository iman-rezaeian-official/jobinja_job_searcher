import os
import pickle

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import COOKIE_FILE


def create_driver():
    options = Options()

    options.add_argument("--start-maximized")

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    return webdriver.Chrome(options=options)


def save_cookies(driver):
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)


def load_cookies(driver):
    if not os.path.exists(COOKIE_FILE):
        return False

    with open(COOKIE_FILE, "rb") as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass

    return True


def manual_login_if_needed(driver):
    driver.get("https://jobinja.ir")

    loaded = load_cookies(driver)

    if loaded:
        driver.refresh()
        time.sleep(3)

        # If cookies valid, skip manual login
        if "login" not in driver.current_url.lower():
            return

    # Manual login flow
    driver.get("https://jobinja.ir/login/user")

    input("Log in manually in opened browser, then press ENTER here...")

    save_cookies(driver)

    driver.get("https://jobinja.ir")


# def create_authenticated_session():
#     cookies = load_cookies()
#
#     if not cookies:
#         manual_login_if_needed()
#
#         cookies = load_cookies()
#
#     session = requests.Session()
#
#     for cookie in cookies:
#         session.cookies.set(
#             cookie["name"],
#             cookie["value"]
#         )
#
#     return session
