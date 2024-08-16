import logging
from typing import TypeVar, Type, Tuple

from RPA.Browser.Selenium import Selenium

from src.exceptions import WrongLocation

T = TypeVar("T", bound="Driver")


class Driver:
    FIELD_MAPPER = {}

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

    def overwrite_driver(self, driver: Selenium) -> None:
        self._driver = driver

    def navigate_to(self, url: str, element_to_wait_for: Tuple[str, str]) -> None:
        self.logger.info(f"Navigating to {url}")
        self.driver.go_to(url)
        self.driver.wait_for_expected_condition(
            "visibility_of_element_located", element_to_wait_for
        )
        if self.driver.is_location(url):
            self.logger.info("Page loaded")
        else:
            raise WrongLocation
