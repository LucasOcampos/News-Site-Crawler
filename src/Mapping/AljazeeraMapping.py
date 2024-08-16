from selenium.webdriver.common.by import By

from src.driver import Driver


class AljazeeraMapping(Driver):
    HOME_URL = "https://www.aljazeera.com/"

    FIELD_MAPPER = {
        "Header": {
            "Site Logo": {
                "by": By.CLASS_NAME,
                "tagname": "span",
                "identifier": "site-logo",
            },
            "Search Button": {
                "by": By.CSS_SELECTOR,
                "tagname": "button",
                "identifier": "div.site-header__search-trigger + button",
            },
        },
        "Search Bar": {
            "Input": {
                "by": By.CSS_SELECTOR,
                "tagname": "input",
                "identifier": "div.search-bar__input-container + input",
            },
            "Button": {
                "by": By.CSS_SELECTOR,
                "tagname": "button",
                "identifier": "div.search-bar__button + button",
            },
        },
        "Results Page": {
            "Sort": {
                "by": By.CLASS_NAME,
                "tagname": "select",
                "identifier": "search-sort-option",
            },
        },
    }

    _SELECT_OPTIONS_MAPPER = {"search-sort-option": []}
