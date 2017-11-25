# -*- coding: utf-8 -*-

import re
import random
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ToredabiCrawler.parameter import (
    mainURL, loginPath, suggestPath, PositionHoldPath, orderPath,
    dashboardsPath,
)


class TradeDerby(object):
    def __init__(self, account, config):
        self.username = account["username"]
        self.password = account["password"]
        self.debug = config["debug"]
        self.headless = config["headless"]

        self.columnsHold = [
            "name", "URL", "rateDay", "rateHold", "sellURL", "quantity",
            "star", "safety", "unitPrice",
        ]
        self.hold = pd.DataFrame(columns=self.columnsHold)
        self.orderURL = {}
        self.asset = 0
        self.status = False

        options = Options()
        if self.headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        self.driver.get(mainURL)

        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success init")

    def login(self):
        loginURL = mainURL + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success login")

    def _getSuggestedURL(self):
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
        if len(key) == 0:
            return False
        else:
            url = stock[key[0]]
            return key[0], url

    def getStatus(self):
        self.driver.get(mainURL + dashboardsPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        self.asset = int(soup.select(".leftTable")[0].select(
            ".downRow")[2].select(".alR")[0].text[:-1].replace(",", ""))
        self.status = False if soup.select(".state_3")[0].select(
            ".state_body")[0].text == u"終了" else True

        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success get status")

    def showStatus(self):
        print("asset :", self.asset)
        print("status:", self.status)

    def showOrder(self):
        for i in range(len(self.orderURL)):
            print(list(self.orderURL.keys())[i])

    def showPositionHold(self):
        columnsShow = [i for i in self.columnsHold if "URL" not in i]
        print(self.hold[columnsShow])

    def updatePositionHold(self):
        self.hold = pd.DataFrame(columns=self.columnsHold)

        self.driver.get(mainURL + PositionHoldPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.select(".stockData"):
            try:
                tagQuote = tag.find(href=re.compile("/td/quotes"))
                stockName = tagQuote.text
                url = mainURL + tagQuote.get("href")
                tagALR = tag.select(".alR")
                rateDay = float(tagALR[len(tagALR) - 2].text[:-2])
                rateOwn = float(tagALR[len(tagALR) - 1].text[:-2])
                sellURL = mainURL + tag.select(".sell")[0].get("href")
                quantity = tagALR[0].text
                star = -3
                for i in range(-2, 3):
                    star = tag.select(".omamoriSuggest")[0].select(
                        ".omamoriSuggestStar" + str(i))
                    if len(star) != 0:
                        star = i
                        break
                safety = True if len(
                    tag.select(".omamoriSafety")[0]) != 0 else False
                unitPrice = tagALR[2].text
                self.hold = self.hold.append(
                    pd.DataFrame(
                        [[stockName, url, rateDay, rateOwn, sellURL, quantity,
                          star, safety, unitPrice]],
                        columns=self.columnsHold,
                    ), ignore_index=True
                )
            except IndexError:
                pass
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success updatePositionHold")

    def updateOrder(self):
        self.orderURL = {}

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
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success update order")

    def _buy(self, name, url):
        self.driver.get(url)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success buy: ", name)

    def _sell(self, name, url):
        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success sell: ", name)

    def close(self):
        self.driver.quit()
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success close")

    def buySuggestedStock(self):
        suggested = self._getSuggestedURL()
        if suggested is False:
            if self.debug:
                print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
                print("Fail buy suggested stock: Not found")
            return False
        else:
            self._buy(suggested[0], suggested[1])
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success buy suggested stock")

    def sellRandom(self):
        if len(self.hold) == 0:
            print("There is no stock")
            return False

        idx = random.randint(0, len(self.hold))
        name = self.hold["name"].iloc[idx]
        url = self.hold["sellURL"].iloc[idx]
        self._sell(name, url)
        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success sell random")

    def sellCutLoss(self):
        candidate = self.hold[self.hold["star"] <= 0]
        for i in range(len(candidate)):
            name = candidate.iloc[i].loc["name"]
            url = candidate.iloc[i].loc["sellURL"]
            self._sell(name, url)

        self.hold = self.hold[0 < self.hold["star"]]

        if self.debug:
            print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
            print("Success sell cut loss")

    def sellProfitable(self):
        candidate = self.hold[
            (self.hold["star"] <= 1) & (10 < self.hold["rateHold"][:-2])
        ]
        if len(candidate) == 0:
            if self.debug:
                print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
                print("Fail sell profirable: No candidate")
        else:
            for i in range(len(candidate)):
                name = candidate.iloc[i].loc["name"]
                url = candidate.iloc[i].loc["sellURL"]
                self._sell(name, url)

            self.hold = self.hold[0 < self.hold["star"]]

            if self.debug:
                print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
                print("Success sell cut loss")

    def toredabiRoutine(self):
        self.getStatus()
        if self.status:
            self.updatePositionHold()
            self.buySuggestedStock()
            self.sellProfitable()
            self.sellCutLoss()
            if self.debug:
                print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), end="")
                print("Success routine")
