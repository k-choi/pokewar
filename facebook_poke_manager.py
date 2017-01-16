# Facebook interaction
# - Selenium based interaction

import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
import time
from pyvirtualdisplay import Display
import logging


def page_loaded(driver):
    return driver.find_element_by_tag_name("body") is not None


# FacebookPokeManager class Structure
class FacebookPokeManager:
    display = None
    driver = None
    update_time = None
    s_pokers = None
    str_email = None
    str_pwd = None
    logger = None

    def init_browser(self):
        # Opening the web browser
        self.logger.info("Open a web browser")
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        chrome_options = webdriver.ChromeOptions()
        preferences = {"profile.default_content_setting_values.notifications": 2}  # Block notification windows
        chrome_options.add_experimental_option("prefs", preferences)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.logger.info("A web browser is ready")

    def conduct_fb_login(self):
        self.logger.info("Conducting a Facebook login")
        self.driver.get("https://www.facebook.com")
        wait = ui.WebDriverWait(self.driver, 10)
        wait.until(page_loaded)
        # Finding email and password fields and sending the keys
        email = self.driver.find_element_by_id("email")
        email.send_keys(self.str_email)
        pwd = self.driver.find_element_by_id("pass")
        pwd.send_keys(self.str_pwd)
        pwd.send_keys(Keys.RETURN)
        time.sleep(5)
        self.logger.info("Facebook login done")

    def init_credentials(self):
        #    * Load email_id and pwd from a config file.
        # Read credential on the first line (userid:passwd format)
        with open('credential.txt') as f:
            credential = f.readline().strip().split(':')
        self.str_email, self.str_pwd = credential

    def __init__(self):
        self.logger = logging.getLogger('pokewar')
        update_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        self.init_credentials()
        self.init_browser()
        self.conduct_fb_login()

    def __del__(self):
        self.display.stop()

    # noinspection PyClassHasNoInit
    # class for saving static info

    # Functions
    def find_who_poked_and_poke_back(self, s_poke_back_group):
        logger = logging.getLogger('pokewar')
        # Open Poke page if not on the page. Otherwise, skip to read current pokes
        # Also, refresh totally if an hour has passed from the last refresh.
        if "https://www.facebook.com/pokes" != self.driver.current_url \
                or self.update_time + datetime.timedelta(hours=1) < datetime.datetime.now():
            self.update_time = datetime.datetime.now()
            logger.info("Moving to Facebook pokes page")
            self.driver.get("https://www.facebook.com/pokes")

        # logger.info("Checking pokes received")
        str_new_poke_xpath = '//div[@id="poke_live_new"]/..//div[@class="clearfix"]/*[.//div[@class="_6a"]]'
        str_new_names_xpath = str_new_poke_xpath + '//div[@class="_6a _42us"]//a[1]'
        str_poke_back_xpath = str_new_poke_xpath + '//div[@class="_6a"]/a[1]'

        l_name_el = self.driver.find_elements_by_xpath(str_new_names_xpath)
        l_poke_back_el = self.driver.find_elements_by_xpath(str_poke_back_xpath)

        # logger.info("Current pokes in inbox : {}".format(len(l_name_el)))

        # Show who poked and you haven't poked back.
        l_names = [el.text for el in l_name_el]
        # Check new pokes that wasn't in the previous check
        if self.s_pokers is not None:
            l_new_pokers = list(set(l_names) - self.s_pokers)
        else:
            l_new_pokers = []
        self.s_pokers = set(l_names)

        # Poke back
        l_poked_back_names = []
        for name_area, button in zip(l_name_el, l_poke_back_el):
            str_name = name_area.text
            if str_name.lower() in s_poke_back_group:
                try:
                    button.click()
                    l_poked_back_names.append(str_name)
                    self.s_pokers.remove(str_name)
                    logger.info("You poked {}".format(str_name))
                except WebDriverException as e:
                    logger.info("You failed to poke {}".format(str_name))

        data = {'new_pokers': l_new_pokers, 'pokers': l_names, 'poked_back': l_poked_back_names}
        logger.info(data)
        return data
