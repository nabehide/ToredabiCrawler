from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from parameter import mainURL, loginPath


class TradeDerby(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        self.driver.get(mainURL)

    def login(self):
        loginURL = "https://www.k-zone.co.jp/" + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

    def close(self):
        self.driver.quit()
