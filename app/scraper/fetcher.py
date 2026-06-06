from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_page(driver, url):
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "div.o-listView__itemInfo"
            )
        )
    )

    return driver.page_source
