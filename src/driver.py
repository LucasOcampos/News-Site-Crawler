import logging
from typing import TypeVar, Type, List
from abc import abstractmethod, ABC

from RPA.Browser.Selenium import Selenium
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.exceptions import WrongLocation

T = TypeVar("T", bound="Driver")


class Driver(ABC):
    FIELD_MAPPER = {}
    SELECT_OPTIONS_MAPPER = {}

    def __init__(self):
        self._driver = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._driver is not None:
            self._driver = None
        return False

    @property
    def driver(self):
        if self._driver is None:
            self.logger.info("Creating driver")
            self._driver = Selenium()
            self._driver.open_available_browser(maximized=True)
        return self._driver

    @classmethod
    def create_from_driver(cls, driver: Type[T]) -> T:
        instance_ = cls()
        instance_.overwrite_driver(driver.driver)
        return instance_

    @abstractmethod
    def load_news_cards(self, date_limit: int):
        raise NotImplementedError

    def overwrite_driver(self, driver: Selenium) -> None:
        self._driver = driver

    def wait_for_element(self, by: str, locator: str, timeout: int = 10) -> WebElement:
        ignored_exceptions = (
            NoSuchElementException,
            StaleElementReferenceException,
        )
        return WebDriverWait(
            self.driver.driver, timeout, ignored_exceptions=ignored_exceptions
        ).until(expected_conditions.presence_of_element_located((by, locator)))

    def wait_for_elements(
        self, by: str, locator: str, timeout: int = 10
    ) -> List[WebElement]:
        ignored_exceptions = (
            NoSuchElementException,
            StaleElementReferenceException,
        )
        return WebDriverWait(
            self.driver.driver, timeout, ignored_exceptions=ignored_exceptions
        ).until(expected_conditions.presence_of_all_elements_located((by, locator)))

    def is_page_loaded(self, element_to_wait_for: str):
        self.driver.wait_until_element_is_visible(element_to_wait_for)

    def navigate_to(self, url: str, element_to_wait_for: str) -> None:
        self.logger.info(f"Navigating to {url}")
        self.driver.go_to(url)

        self.is_page_loaded(element_to_wait_for)
        if self.driver.is_location(url):
            self.logger.info("Page loaded")
        else:
            raise WrongLocation

    def close_cookies(self, accept_btn: str) -> None:
        self.driver.click_element_when_clickable(accept_btn)

    def perform_search(
        self,
        search_string: str,
        search_bar_input: str,
        search_button: str,
        element_to_wait_for: str,
        toggle_search_bar_button: str = None,
    ):
        if toggle_search_bar_button:
            self.logger.info("Opening search bar")
            self.driver.click_element_when_clickable(toggle_search_bar_button)

        self.logger.info("Inputting search phrase in search field")
        self.driver.input_text_when_element_is_visible(search_bar_input, search_string)

        self.logger.info("Clicking search button")
        self.driver.click_element_when_clickable(search_button)

        self.is_page_loaded(element_to_wait_for)

    def sort_search(self, sort_element: str, value: str):
        self.logger.info(f"Sorting results list by {value}")
        self.driver.select_from_list_by_value(sort_element, value)

        self.is_page_loaded(sort_element)
