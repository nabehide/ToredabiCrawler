import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from parameter import (
    mainURL, loginPath, suggestPath, PositionHoldPath, orderPath,
)


class TradeDerby(object):
    def __init__(self, username, password, headless=True, debug=False):
        self.username = username
        self.password = password
        self.debug = debug

        self.columnsHold = ["name", "URL", "rateDay", "rateHold", "sellURL"]
        self.hold = pd.DataFrame(columns=self.columnsHold)
        self.orderURL = {}

        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        self.driver.get(mainURL)

        if self.debug:
            print("Success init")

    def login(self):
        loginURL = mainURL + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

        if self.debug:
            print("Success login")

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
            tagALR = tag.select(".alR")
            rateDay = tagALR[len(tagALR) - 2].text
            rateOwn = tagALR[len(tagALR) - 1].text
            sellURL = mainURL + tag.select(".sell")[0].get("href")

            self.hold = self.hold.append(
                pd.DataFrame(
                    [[stockName, url, rateDay, rateOwn, sellURL]],
                    columns=self.columnsHold,
                ), ignore_index=True
            )

    def updateOrder(self):
        self.driver.get(mainURL + orderPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.select(".stockData"):
            try:
                tagsCandidate = tag.select(".alC")
                tagCandidate = tagsCandidate[len(tagsCandidate) - 1].find(
                    href=re.compile("/td/orders"))
                if "edit" in tagCandidate.get("href"):
                    tagQuote = tag.find(href=re.compile("/td/quotes"))
                    stockName = tagQuote.text
                    url = mainURL + tagQuote.get("href")
                    self.orderURL[stockName] = url
            except (TypeError, AttributeError, IndexError):
                pass

    def buy(self, name, url):
        self.driver.get(url)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()
        if self.debug:
            print("Success buy: ", name)

    def sell(self, name, url):
        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()
        if self.debug:
            print("Success sell: ", name)

    def close(self):
        self.driver.quit()
        if self.debug:
            print("Success close")

    def getSuggestedStock(self):
        suggestedName, suggestedURL = self.getSuggestedURL()
        self.buy(suggestedName, suggestedURL)

    def sellRandom(self):
        if len(self.hold) == 0:
            print("There is no stock")
            return False

        idx = np.random.randint(len(self.hold))
        name = self.hold["name"].iloc[idx]
        url = self.hold["sellURL"].iloc[idx]
        self.sell(name, url)
