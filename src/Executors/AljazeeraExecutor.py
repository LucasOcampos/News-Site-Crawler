from src.Mapping.AljazeeraMapping import AljazeeraMapping
from src.driver import Driver
from src.executor import Executor


class AljazeeraExecutor(Executor):
    NEWS_SITE = "aljazeera"
    HOME_URL = AljazeeraMapping.HOME_URL

    def __init__(self, driver: Driver):
        super().__init__(driver)

    def perform_search(self):
        raise NotImplementedError

    def execute(self):
        self.logger.info(f"Opening news site: {self.HOME_URL}")
        aljazeera = AljazeeraMapping.create_from_driver(self._driver)
        aljazeera.navigate_to(
            self.HOME_URL,
            (
                AljazeeraMapping.FIELD_MAPPER["Header"]["Site Logo"]["by"],
                AljazeeraMapping.FIELD_MAPPER["Header"]["Site Logo"]["identifier"],
            ),
        )

        self.perform_search()

        pass
