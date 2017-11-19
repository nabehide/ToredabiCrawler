import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from parameter import mainURL, loginPath, suggestPath, PositionHoldPath


class TradeDerby(object):
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password

        self.hold = {}

        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        self.driver.get(mainURL)

    def login(self):
        loginURL = mainURL + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

    def getSuggestedURL(self):
        self.driver.get(mainURL + suggestPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        stock = {}
        for tag in soup.select(".alC"):
            tagQuote = tag.find(href=re.compile("/td/quotes/"))
            try:
                stockName = tagQuote.text
                url = mainURL + tagQuote.get("href")
                stock[stockName] = url
            except (TypeError, AttributeError):
                pass

        # print(list(stock.keys()))
        key = [i for i in list(stock.keys()) if i.isdigit() and 1500 < int(i)]
        # print("key", key)
        url = stock[key[0]]

        return key[0], url

    def updatePositionHold(self):
        self.driver.get(mainURL + PositionHoldPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.select(".stockData"):
            tagQuote = tag.find(href=re.compile("/td/quotes"))
            stockName = tagQuote.text
            url = mainURL + tagQuote.get("href")
            self.hold[stockName] = url

    def buy(self, name, url):
        self.driver.get(url)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()
        print("Success buy: ", name)

    def close(self):
        self.driver.quit()

    def getSuggestedStock(self):
        suggestedName, suggestedURL = self.getSuggestedURL()
        self.buy(suggestedName, suggestedURL)
