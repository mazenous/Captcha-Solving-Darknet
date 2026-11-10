import logging
import time

from consts import ROOT_DIR
from crawler.dread_crawler import DreadCrawler


# logger
logging.basicConfig(filename=f"{ROOT_DIR}/model_accuracy_logger.log", level=logging.INFO)


def dread_crawl_images_and_enter_values_manually():
    time.sleep(5)
    crawler = DreadCrawler()
    crawler.wait_in_queue_until(90, 5)
    crawler.crawl_captcha_images()
    time.sleep(2)
    crawler.close()


def dread_enter_values_from_model():
    time.sleep(5)
    crawler = DreadCrawler()
    crawler.wait_in_queue_until(90, 5)
    time.sleep(2)
    crawler.enter_captcha_values()
    time.sleep(2)
    crawler.close()
