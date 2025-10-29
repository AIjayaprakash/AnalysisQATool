from selenium.webdriver.common.by import By
from state import state

def get_driver():
    if state.current_session and state.current_session in state.drivers:
        return state.drivers[state.current_session]
    raise Exception("No active browser session")

def get_locator(by: str, value: str):
    mapping = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    return mapping[by.lower()], value
