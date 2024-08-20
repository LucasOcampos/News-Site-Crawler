from src.Mapping.AljazeeraMapping import AljazeeraMapping
from src.driver import Driver
from src.executor import Executor


class AljazeeraExecutor(Executor):
    NEWS_SITE = "aljazeera"
    HOME_URL = AljazeeraMapping.HOME_URL

    def __init__(self, driver: Driver, search_phrase: str, num_months: int):
        super().__init__(driver, search_phrase, num_months)

    def execute(self):
        self.logger.info(f"Opening news site: {self.HOME_URL}")
        aljazeera = AljazeeraMapping.create_from_driver(self._driver)
        aljazeera.navigate_to(
            self.HOME_URL,
            AljazeeraMapping.FIELD_MAPPER["Header"]["Site Logo"],
        )

        aljazeera.close_cookies(AljazeeraMapping.FIELD_MAPPER["Cookies"]["Accept"])

        aljazeera.perform_search(
            self._search_phrase,
            AljazeeraMapping.FIELD_MAPPER["Search Bar"]["Input"],
            AljazeeraMapping.FIELD_MAPPER["Search Bar"]["Search Button"],
            AljazeeraMapping.FIELD_MAPPER["Results Page"]["Results Amount"],
            AljazeeraMapping.FIELD_MAPPER["Header"]["Search Button"],
        )

        aljazeera.sort_search(
            AljazeeraMapping.FIELD_MAPPER["Results Page"]["Sort"],
            AljazeeraMapping.SELECT_OPTIONS_MAPPER[
                AljazeeraMapping.FIELD_MAPPER["Results Page"]["Sort"]
            ][0],
        )

        aljazeera.load_news_cards(self._num_months)
        aljazeera.save_data(self._num_months, self._search_phrase)
