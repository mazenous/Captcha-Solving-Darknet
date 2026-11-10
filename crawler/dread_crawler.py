import logging
import os
import time
import warnings
from datetime import datetime
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



from consts import tor_default_settings_path, tor_binary_path, dread_link, crawled_data_path, allow_duplicates, \
    nr_login_repetition, browser_timeout
from crawler.crawler_helper import logger
from neural_network.test_network import get_model, prepare_image_4_prediction, decode_model_result


class DreadCrawler:

    def __init__(self):
        # browser options in order to use TOR with geckodriver/Firefox and add preferences
        self.options = Options()

        # disable TOR to popup
        # self.options.add_argument('--headless')
        # use default preferences to bypass confirm popup after launching TOR
        self.profile = FirefoxProfile(tor_default_settings_path)
        self.profile.update_preferences()
        self.options.profile = self.profile

        # TOR binary to use it as a webdriver
        self.options.binary = tor_binary_path

        print("Initializing crawler")
        self.browser = webdriver.Firefox(self.options)
        time.sleep(5)
        self.nr_repetition = nr_login_repetition
        self.browser.get(dread_link)
        # TODO: add some wait statement in case the website didn't load
        time.sleep(5)
        # driver.delete_all_cookies()
        self.session_time = int(datetime.now().timestamp())

    def close(self):
        self.browser.close()

    # TODO: add try except wrapper
    def get_input_field_by_index(self, idx):
        xpath = f'//input[@name="c{idx}"]'
        # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_element_located(
        #     (By.XPATH, xpath)))
        return self.browser.find_element(By.XPATH, xpath)

    def get_input_captcha(self):
        # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_element_located(
        #     (By.CLASS_NAME, "image")))
        return self.browser.find_element(By.CLASS_NAME, "image")

    def get_submit_button(self):
        for i in range(5):
            time.sleep(1)
            try:
                # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_element_located(
                #     (By.CSS_SELECTOR, "button.before")))
                return self.browser.find_element(By.CSS_SELECTOR, "button.before")
            except WebDriverException:
                print("There is a problem while getting submit button")
        raise WebDriverException("There is a problem while getting submit button")

    def get_refresh_button(self):
        # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR, "button.expired")))
        return self.browser.find_element(By.CSS_SELECTOR, "button.expired")

    def find_elements_by_class_name(self, cls_name):
        # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_all_elements_located(
        #     (By.CLASS_NAME, cls_name)))
        return self.browser.find_elements(By.CLASS_NAME, cls_name)

    def find_elements_by_css_selector(self, css_selector):
        # WebDriverWait(self.browser, browser_timeout).until(EC.presence_of_all_elements_located(
        #     (By.CSS_SELECTOR, css_selector)))
        return self.browser.find_elements(By.CSS_SELECTOR, css_selector)

    @logger
    def wait_in_queue_until(self, until, step, count=0):
        # check if I'm even in a queue, otherwise just continue
        if len(self.find_elements_by_class_name("queue-graphic")) == 0:
            time.sleep(step)
            return
        elif count < until:
            time.sleep(step)
            count = count + step
            self.wait_in_queue_until(until, step, count)
        else:
            warnings.warn("It's taking too long in the queue, quitting...")
            self.close()

    @logger
    def wait_until_captcha_fields_change(self, wait_time=40):

        def fields_changed():
            changed = True
            for i in range(1, 7):
                inpt = self.get_input_field_by_index(i)
                changed = changed and "-" != inpt.get_property("value")
            return changed

        if not (wait_time > 0) or fields_changed():
            return
        else:
            time.sleep(5)
            self.wait_until_captcha_fields_change(wait_time - 5)

    def get_captcha_images(self):
        images = []
        for i in range(1, 7):
            inpt = self.get_input_field_by_index(i)
            inpt.send_keys("-")

            time.sleep(2)
            img = self.get_input_captcha()
            png = img.screenshot_as_png
            images.append(Image.open(BytesIO(png)))
        return images

    def get_captcha_input_values(self):
        inputs = []
        for i in range(1, 7):
            inpt = self.get_input_field_by_index(i)
            inputs.append(inpt.get_property("value"))
        return inputs

    def enter_captcha_values(self):
        now = int(datetime.now().timestamp())
        btn_submit = self.get_submit_button()
        images = self.get_captcha_images()
        # get model and predict values
        model = get_model()
        vals = []
        for img in images:
            inpt = self.get_input_field_by_index(images.index(img) + 1)
            img = prepare_image_4_prediction(img)
            value = decode_model_result(model(img))
            inpt.clear()
            inpt.send_keys(value)
            time.sleep(2)
            vals.append(value)

        vals = ''.join(vals)
        btn_submit.click()
        time.sleep(3)
        entered = len(self.find_elements_by_css_selector("div.filterSettings")) != 0
        msg = f"Entering Dread at {self.session_time} with input {vals}"
        if entered:
            logging.info(f'SUCCESS: {msg}')
        else:
            # avoid repeating forever, just max 10 times
            logging.info(f'FAIL: {msg}')
            if self.nr_repetition > 0:
                self.nr_repetition -= 1
                self.wait_in_queue_until(90, 5)
                self.enter_captcha_values()

    @logger
    def crawl_captcha_images(self):
        # it should just get the images and save them firstly in a list after that and before submitting the answer
        # it should retrieve the input values and save them as well in a list if I couldn't enter I should repeat and
        # clear the both lists otherwise it can save the 6 images
        now = int(datetime.now().timestamp())
        btn_submit = self.get_submit_button()
        #btn_refresh = self.get_refresh_button()
        images = self.get_captcha_images()
        # wait until the fields are changed
        self.wait_until_captcha_fields_change()
        # HERE it's necessary to find out the values of each picture and enter them manually
        # After input the values I should retrieve them and save them in the list
        inputs = self.get_captcha_input_values()

        # Now I should try to submit my answer and checkout if I entered
        folder_name = ''.join(inputs).upper()
        if not allow_duplicates and folder_name in os.listdir(crawled_data_path):
            print(f"Similar images with the same label {folder_name} already exist")
            print("entering fake values")
            inpt = self.get_input_field_by_index(2)
            inpt.clear()
            inpt.send_keys("E")

        btn_submit.click()
        time.sleep(3)
        entered = len(self.find_elements_by_css_selector("div.filterSettings")) != 0
        path = f"{crawled_data_path}/{folder_name}"
        if entered:
            if not os.path.exists(path):
                os.mkdir(path)
                print(f"Saving images {folder_name}")
                for j in range(6):
                    images[j].save(f"{path}/{now}_{j}_{inputs[j].capitalize()}.png")
                # If I want to do it multiple times I should close the browser and reopen it here

            # If the path already exists that means the samples exist already
            # and there is no need to save them again
            else:
                print(f"There are similar images for {folder_name}")
                return
        elif not entered and self.nr_repetition > 0:
            print("Images not saved, repeating...")
            self.nr_repetition -= 1
            self.wait_in_queue_until(90, 1)
            self.crawl_captcha_images()
        else:
            return
