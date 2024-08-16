import logging
from abc import abstractmethod, ABC
from typing import Type

from src.driver import Driver
from src.exceptions import WrongLocation


class Executor(ABC):
    NEWS_SITE = None
    HOME_URL = None

    def __init__(self, driver: Driver):
        self._driver = driver
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @classmethod
    def init_driver(cls) -> Type[Driver]:
        Driver.__abstractmethods__ = {}
        return Driver

    def __call__(self):
        status = {}
        try:
            self.execute()
        except WrongLocation as e:
            self.logger.debug(e, exc_info=True)
        except KeyboardInterrupt:
            self.logger.info("Exiting execution safely")
        except Exception as e:
            self.logger.error(e, exc_info=True)
        return status

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def perform_search(self):
        raise NotImplementedError
