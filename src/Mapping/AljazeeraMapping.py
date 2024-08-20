import os
import re

from datetime import datetime, timedelta
from typing import List

import pandas as pd
import requests
from selenium.common import NoSuchElementException, StaleElementReferenceException

from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By

from src.driver import Driver


class AljazeeraMapping(Driver):
    HOME_URL = "https://www.aljazeera.com/"

    FIELD_MAPPER = {
        "Header": {
            "Site Logo": "class:site-logo",
            "Search Button": "css:div.site-header__search-trigger > button",
        },
        "Search Bar": {
            "Input": "css:div.search-bar__input-container > input",
            "Search Button": "css:div.search-bar__button > button",
        },
        "Results Page": {
            "Results Amount": "class:search-summary__query",
            "Sort": "id:search-sort-option",
            "News Card": "css:article.u-clickable-card:has(div.gc__content > footer > div.gc__meta > div.gc__date)",
            "Show More Button": "css:button.show-more-button",
            "Loading More News": "css:button.show-more-button-loading",
        },
        "News Card": {
            "Title": "css:article.u-clickable-card:has(div.gc__content > footer > div.gc__meta > div.gc__date) h3.gc__title > a.u-clickable-card__link > span",
            "Description": "css:article.u-clickable-card:has(div.gc__content > footer > div.gc__meta > div.gc__date) div.gc__excerpt > p",
            "Picture": "css:article.u-clickable-card:has(div.gc__content > footer > div.gc__meta > div.gc__date) div.responsive-image > img",
            "Date": "css:article.u-clickable-card:has(div.gc__content > footer > div.gc__meta > div.gc__date) div.date-simple > span:first-child",
        },
        "Cookies": {"Accept": "id:onetrust-accept-btn-handler"},
    }

    SELECT_OPTIONS_MAPPER = {"id:search-sort-option": ["date", "relevance"]}

    def __init__(self):
        super().__init__()

    def get_date_limit(self, num_of_months: int) -> datetime:
        return datetime.now() - timedelta(days=30 * num_of_months)

    def load_news_cards(self, date_limit: int) -> None:
        date_limit = self.get_date_limit(date_limit)
        last_news_date = datetime.now()

        while last_news_date >= date_limit:
            self.logger.info("Getting all news cards")
            news_card = self.driver.find_elements(
                self.FIELD_MAPPER["Results Page"]["News Card"]
            )[-1]

            self.logger.info("Getting date of the last news card")
            date = self.driver.find_element(
                self.FIELD_MAPPER["News Card"]["Date"], news_card
            ).text

            date = re.search(r"\d{1,2}\s[A-Za-z]{3}\s\d{4}", date).group()

            last_news_date = datetime.strptime(date, "%d %b %Y")
            self.logger.info(last_news_date)

            if last_news_date >= date_limit:
                self.logger.info("Clicking the Show More Button")
                self.driver.wait_until_page_contains_element(
                    self.FIELD_MAPPER["Results Page"]["Show More Button"]
                )
                show_more_button = self.driver.find_element(
                    self.FIELD_MAPPER["Results Page"]["Show More Button"]
                )
                scroll_origin = ScrollOrigin.from_element(show_more_button)
                ActionChains(self.driver.driver).scroll_from_origin(
                    scroll_origin, 0, 300
                ).perform()

                self.driver.click_element_when_clickable(
                    self.FIELD_MAPPER["Results Page"]["Show More Button"]
                )
                self.driver.wait_until_page_does_not_contain_element(
                    self.FIELD_MAPPER["Results Page"]["Loading More News"]
                )

    def collect_data_from_element(self, field: str, is_img: bool = False) -> List[str]:
        element = self.driver.find_element(field)
        scroll_origin = ScrollOrigin.from_element(element)
        ActionChains(self.driver.driver).scroll_from_origin(
            scroll_origin, 0, 300
        ).perform()

        for i in range(5):
            try:
                self.logger.info(f"Collecting data from {field}")
                self.wait_for_elements(By.CSS_SELECTOR, field.replace("css:", ""))
                if is_img:
                    return [
                        element.get_attribute("src")
                        for element in self.driver.find_elements(field)
                    ]
                return [element.text for element in self.driver.find_elements(field)]
            except (NoSuchElementException, StaleElementReferenceException):
                self.logger.info(
                    f"Tried to fetch data from {field} but was unable to.  Retrying {i + 1}/5"
                )

    def collect_data(self) -> pd.DataFrame:
        card_data = {
            "Title": self.collect_data_from_element(
                self.FIELD_MAPPER["News Card"]["Title"]
            ),
            "Description": self.collect_data_from_element(
                self.FIELD_MAPPER["News Card"]["Description"]
            ),
            "Picture": self.collect_data_from_element(
                self.FIELD_MAPPER["News Card"]["Picture"], True
            ),
            "Date": self.collect_data_from_element(
                self.FIELD_MAPPER["News Card"]["Date"]
            ),
        }

        self.logger.info(card_data)

        return pd.DataFrame(card_data)

    def save_data(self, date_limit: int, search_string: str):
        self.is_page_loaded(self.FIELD_MAPPER["Results Page"]["Results Amount"])
        date_limit = self.get_date_limit(date_limit)

        data = self.collect_data()
        for _, row in data.iterrows():
            date = re.search(r"\d{1,2}\s[A-Za-z]{3}\s\d{4}", row["Date"]).group()
            row["Date"] = datetime.strptime(date, "%d %b %Y")

        data = data[data["Date"] >= date_limit]

        data = self.count_search_phrases(data, search_string)
        data = self.contains_money(data)
        data = self.download_news_picture(data)

        os.makedirs(f"{os.getcwd()}/output", exist_ok=True)

        data.to_csv(f"{os.getcwd()}/output/data.csv", index=False)

    def count_search_phrases(
        self, data: pd.DataFrame, search_string: str
    ) -> pd.DataFrame:
        new_col_data = []
        for _, row in data.iterrows():
            count = 0
            count += row["Title"].count(search_string)
            count += row["Description"].count(search_string)
            new_col_data.append(count * 1.0)

        data["Search Phrase Count"] = new_col_data
        return data

    def contains_money(self, data: pd.DataFrame) -> pd.DataFrame:
        new_col_data = []
        for _, row in data.iterrows():
            if re.search(r"([£$€])(\d+(?:\.\d{2})?)", row["Title"]):
                new_col_data.append(True)
            elif re.search(r"([£$€])(\d+(?:\.\d{2})?)", row["Description"]):
                new_col_data.append(True)
            else:
                new_col_data.append(False)

        data["Contains Money"] = new_col_data
        return data

    def download_news_picture(self, data: pd.DataFrame) -> pd.DataFrame:
        new_col_data = []
        for i, row in data.iterrows():
            image_path = os.path.join(f"{os.getcwd()}/files", f"image_{i}.png")
            image_data = requests.get(row["Picture"])
            with open(image_path, "wb") as f:
                f.write(image_data.content)

            new_col_data.append(image_path)

        data["Picture Path"] = new_col_data
        return data
