import logging
import os
import shutil
from datetime import datetime, timedelta
from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems

from src.executor import Executor

logs_directory = os.path.join(os.getcwd(), r"output", r"logs")
os.makedirs(logs_directory, exist_ok=True)

log_file = f'{datetime.now().strftime("%Y_%m_%d")}.log'
log_file_path = os.path.join(logs_directory, log_file)

downloaded_files_dir = os.path.join(os.getcwd(), r"files")
os.makedirs(downloaded_files_dir, exist_ok=True)

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

wi = WorkItems()
wi.get_input_work_item()
search_phrase = wi.get_work_item_variable("search_phrase")
num_months = wi.get_work_item_variable("num_months")


@task()
def aljazeera():
    subclasses = {sub.NEWS_SITE: sub for sub in Executor.__subclasses__()}

    with Executor.init_driver()() as driver:
        executor = subclasses["aljazeera"](driver, search_phrase, num_months)
        executor()

    cleanup_files()
    cleanup_files(path=downloaded_files_dir)


@task()
def run():
    subclasses = {sub.NEWS_SITE: sub for sub in Executor.__subclasses__()}

    with Executor.init_driver()() as driver:
        for news_site in list(subclasses.keys()):
            executor = subclasses[news_site](driver, search_phrase, num_months)
            executor()

    cleanup_files()
    cleanup_files(path=downloaded_files_dir)


def cleanup_files(dt: timedelta = timedelta(weeks=4), path: str = logs_directory):
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        if (
            timedelta(seconds=datetime.now().timestamp() - os.path.getmtime(file_path))
            >= dt
        ):
            logger.info(f"Removing file {file_path}")
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
