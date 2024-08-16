import argparse
import logging
import os
from datetime import datetime
from robocorp.tasks import task

from src.executor import Executor

os.makedirs(os.path.join(os.getcwd(), r"logs"), exist_ok=True)

logs_directory = os.path.join(os.getcwd(), r"logs")

log_file = f'{datetime.now().strftime("%Y_%m_%d")}.log'
log_file_path = os.path.join(logs_directory, log_file)

logging.basicConfig(
    style="{",
    format="{asctime} [{levelname}] {name} {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    force=True,
    handlers=[
        logging.FileHandler(
            filename=log_file_path,
            encoding="utf-8",
            mode="a+",
        ),
    ],
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@task(this_is_option='aljazeera')
def aljazeera():
    subclasses = {sub.NEWS_SITE: sub for sub in Executor.__subclasses__()}

    with Executor.init_driver()() as driver:
        executor = subclasses['aljazeera'](driver)
        status = executor()


@task(this_is_option='all')
def run():
    subclasses = {sub.NEWS_SITE: sub for sub in Executor.__subclasses__()}

    with Executor.init_driver()() as driver:
        for news_site in list(subclasses.keys()):
            executor = subclasses[news_site](driver)
            status = executor()
