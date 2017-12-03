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

        self.options = Options()
        if self.headless:
            self.options.add_argument("--headless")

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success init"
        if self.debug:
            print(message)

    def open(self):
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=self.options)
        self.driver.get(mainURL)

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success open"
        if self.debug:
            print(message)
        return message

    def login(self):
        loginURL = mainURL + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success login"
        if self.debug:
            print(message)
        return message

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

        key = [i for i in list(stock.keys()) if i.isdigit() and 1500 < int(i)]
        extractedKey = []
        for i in key:
            flag = True
            for j in list(self.orderURL):
                if i in j:
                    flag = False
                    break
            for j in list(self.hold["name"]):
                if flag and i in j:
                    flag = False
                    break
            if flag:
                extractedKey.append(i)
        if len(extractedKey) == 0:
            return False
        else:
            url = stock[extractedKey[0]]
            return extractedKey[0], url

    def getStatus(self):
        self.driver.get(mainURL + dashboardsPath)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        try:
            self.asset = int(soup.select(".leftTable")[0].select(
                ".downRow")[2].select(".alR")[0].text[:-1].replace(",", ""))
            self.status = True if soup.select(".state_1")[0].select(
                ".stock_market_title")[0].text == u"現在の東証市場" else False
        except IndexError:
            self.status = False

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success get status"
        if self.debug:
            print(message)
        return message

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

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success updatePositionHold"
        if self.debug:
            print(message)
        return message

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

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success update order"
        if self.debug:
            print(message)
        return message

    def _buy(self, name, url):
        self.driver.get(url)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success buy: " + name
        if self.debug:
            print(message)
        return message

    def _sell(self, name, url):
        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success sell: " + name
        if self.debug:
            print(message)
        return message

    def close(self):
        self.driver.quit()

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success close"
        if self.debug:
            print(message)
        return message

    def buySuggestedStock(self):
        suggested = self._getSuggestedURL()
        if suggested is False:
            message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Fail buy suggested stock: Not found"
            if self.debug:
                print(message)
            return message
        else:
            self._buy(suggested[0], suggested[1])

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success buy suggested stock"
        if self.debug:
            print(message)
        return message

    def sellRandom(self):
        if len(self.hold) == 0:
            print("There is no stock")
            return False

        idx = random.randint(0, len(self.hold))
        name = self.hold["name"].iloc[idx]
        url = self.hold["sellURL"].iloc[idx]
        self._sell(name, url)

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success sell random"
        if self.debug:
            print(message)
        return message

    def sellCutLoss(self):
        candidate = self.hold[self.hold["star"] <= 0]
        for i in range(len(candidate)):
            name = candidate.iloc[i].loc["name"]
            url = candidate.iloc[i].loc["sellURL"]
            self._sell(name, url)

        self.hold = self.hold[0 < self.hold["star"]]

        message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success sell cut loss"
        if self.debug:
            print(message)
        return message

    def sellProfitable(self):
        candidate = self.hold[
            (self.hold["star"] <= 1) & (10 < self.hold["rateHold"][:-2])
        ]
        if len(candidate) == 0:
            message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Fail sell profirable: No candidate"
            if self.debug:
                print(message)
            return message
        else:
            for i in range(len(candidate)):
                name = candidate.iloc[i].loc["name"]
                url = candidate.iloc[i].loc["sellURL"]
                self._sell(name, url)

            self.hold = self.hold[0 < self.hold["star"]]

            message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success sell cut loss"
            if self.debug:
                print(message)
            return message

    def toredabiRoutine(self):
        self.getStatus()
        if self.status:
            ret = ""
            ret += self.updatePositionHold() + "\n"
            ret += self.updateOrder() + "\n"
            ret += self.buySuggestedStock() + "\n"
            ret += self.sellProfitable() + "\n"
            ret += self.sellCutLoss() + "\n"

            message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Success routine"
            if self.debug:
                print(message)
            return ret + message
        else:
            message = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + "Fail routine: Closed"
            if self.debug:
                print(message)
            return message
