import argparse
import logging
import os
from datetime import datetime

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

if __name__ == "__main__":
    subclasses = {sub.NEWS_SITE: sub for sub in Executor.__subclasses__()}

    parser = argparse.ArgumentParser()
    parser.add_argument("news_site")
    arg = parser.parse_args()

    with Executor.init_driver()() as driver:
        executor = subclasses[arg.news_site](driver)
        status = executor()
