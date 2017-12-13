# -*- coding: utf-8 -*-

import re
import random
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from TradeDerPy.parameter import (
    mainURL, loginPath, suggestPath, PositionHoldPath, orderPath,
    dashboardsPath,
)


def timeStamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")


class TradeDerPy(object):

    def __init__(self, account, config):
        self.username = account["username"]
        self.password = account["password"]
        self.debug = config["debug"]
        self.headless = config["headless"]
        self.driverPath = config["driverPath"]

        self.columnsHold = [
            "name", "URL", "rateDay", "rateHold", "sellURL", "quantity",
            "star", "safety", "unitPrice",
        ]
        self.hold = pd.DataFrame(columns=self.columnsHold)
        self.columnsSuggested = [
            "name", "URL",
        ]
        self.suggested = pd.DataFrame(columns=self.columnsSuggested)
        self.orderURL = {}
        self.asset = 0
        self.power = 0
        self.status = False

        self.options = Options()
        if self.headless:
            self.options.add_argument("--headless")

        message = timeStamp() + "Success init"
        if self.debug:
            print(message)

    def open(self):
        self.driver = webdriver.Chrome(
            self.driverPath, chrome_options=self.options)
        self.driver.get(mainURL)

        message = timeStamp() + "Success open"
        if self.debug:
            print(message)
        return message

    def login(self):
        loginURL = mainURL + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

        message = timeStamp() + "Success login"
        if self.debug:
            print(message)
        return message

    def buy(self, name, maximum):
        self.driver.get(mainURL + "/td/quotes/" + name + "T")
        soup, text = self._getSoupText()
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        soup, text = self._getSoupText()
        unit = int(soup.select(".boxb")[0].find(
                   id="hd_stock").text.replace(",", ""))
        minimumPrice = int(soup.select(".entxt_r")[0].find(
                           id="b_price").text.replace(",", ""))
        # maximumPrice = int(soup.select(".entxt_r")[1].find(
        #                    id="power").text.replace(",", ""))
        if 0 < minimumPrice:
            purchase = unit * int(maximum / minimumPrice)
        else:
            purchase = 0
        if 0 < purchase:
            self.driver.find_element_by_id(
                "order_com1_volume").send_keys(str(purchase))

            self.driver.find_element_by_class_name("transition").click()
            self.driver.find_elements_by_class_name("transition")[1].click()

            message = timeStamp() + "Success buy: " + name
        else:
            message = (timeStamp() + "Fail buy: " +
                       name + " not have enough money")
        if self.debug:
            print(message)
        return message

    def sell(self, name, url, quantity):
        self.driver.get(url)
        self.driver.find_element_by_id(
            "order_com1_volume").send_keys(str(quantity))
        # soup, text = self._getSoupText()
        # maximum = soup.select(
        #     ".enkotei")[1].select(".entxt_r")[0].text.replace(",", "")
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()

        message = timeStamp() + "Success sell: " + name
        if self.debug:
            print(message)
        return message

    def close(self):
        self.driver.quit()

        message = timeStamp() + "Success close"
        if self.debug:
            print(message)
        return message

    def getStatus(self):
        self.driver.get(mainURL + dashboardsPath)
        soup, text = self._getSoupText()
        try:
            self.status = False
            self.asset = int(soup.select(".leftTable")[0].select(
                ".downRow")[0].select(".alR")[0].text[:-1].replace(",", ""))
            self.power = int(soup.select(".leftTable")[0].select(
                ".downRow")[2].select(".alR")[0].text[:-1].replace(",", ""))
            if 0 < len(soup.select(".state_1")):
                self.status = True if soup.select(".state_1")[0].select(
                    ".stock_market_title")[0].text == u"現在の東証市場" else False
            if 0 < len(soup.select(".state_2")) and not self.status:
                self.status = True if soup.select(".state_2")[0].select(
                    ".stock_market_title")[0].text == u"現在の東証市場" else False
        except IndexError:
            self.status = False

        message = timeStamp() + "Success get status"
        if self.debug:
            print(message)
        return message

    def showStatus(self):
        print("asset :", self.asset)
        print("power :", self.power)
        print("status:", self.status)

    def getOrder(self):
        self.orderURL = {}

        self.driver.get(mainURL + orderPath)
        soup, text = self._getSoupText()
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

        message = timeStamp() + "Success get order"
        if self.debug:
            print(message)
        return message

    def showOrder(self):
        for i in range(len(self.orderURL)):
            print(list(self.orderURL.keys())[i])

    def getHold(self):
        self.hold = pd.DataFrame(columns=self.columnsHold)

        self.driver.get(mainURL + PositionHoldPath)
        soup, text = self._getSoupText()
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

        message = timeStamp() + "Success get Hold"
        if self.debug:
            print(message)
        return message

    def showHold(self):
        columnsShow = [i for i in self.columnsHold if "URL" not in i]
        print(self.hold[columnsShow])

    def getSuggested(self):
        self.suggested = pd.DataFrame(columns=self.columnsSuggested)

        self.driver.get(mainURL + suggestPath)
        soup, text = self._getSoupText()
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
        for i in extractedKey:
            self.suggested = self.suggested.append(
                pd.DataFrame([[i, stock[i]]], columns=self.columnsSuggested),
                ignore_index=True,
            )

        message = timeStamp() + "Success get suggested"
        if self.debug:
            print(message)
        return message

    def showSuggested(self):
        print(self.suggested)

    def buySuggestedStock(self):
        if len(self.suggested) == 0:
            message = timeStamp() + "Fail buy suggested stock: Not found"
            if self.debug:
                print(message)
            return message
        else:
            # idx = random.randint(0, len(self.suggested) - 1)
            for idx in range(len(self.suggested)):
                ret = self.buy(
                    self.suggested["name"][idx], self.asset * 0.05,
                )
                if "Fail" in ret:
                    break

        message = timeStamp() + "Success buy suggested stock"
        if self.debug:
            print(message)
        return message

    def sellRandom(self):
        if len(self.hold) == 0:
            print("There is no stock")
            return False

        idx = random.randint(0, len(self.hold) - 1)
        name = self.hold["name"].iloc[idx]
        url = self.hold["sellURL"].iloc[idx]
        quantity = self.hold["quantity"].iloc[idx]
        self.sell(name, url, quantity)

        message = timeStamp() + "Success sell random"
        if self.debug:
            print(message)
        return message

    def sellCutLoss(self):
        candidate = self.hold[self.hold["star"] <= 0]
        for i in range(len(candidate)):
            name = candidate.iloc[i].loc["name"]
            url = candidate.iloc[i].loc["sellURL"]
            quantity = candidate.iloc[i].loc["quantity"]
            self.sell(name, url, quantity)

        self.hold = self.hold[0 < self.hold["star"]]

        message = timeStamp() + "Success sell cut loss"
        if self.debug:
            print(message)
        return message

    def sellProfitable(self):
        candidate = self.hold[
            (self.hold["star"] <= 1) & (10 < self.hold["rateHold"][:-2])
        ]
        if len(candidate) == 0:
            message = timeStamp() + "Fail sell profirable: No candidate"
            if self.debug:
                print(message)
            return message
        else:
            for i in range(len(candidate)):
                name = candidate.iloc[i].loc["name"]
                url = candidate.iloc[i].loc["sellURL"]
                quantity = candidate.iloc[i].loc["quantity"]
                self.sell(name, url, quantity)

            self.hold = self.hold[0 < self.hold["star"]]

            message = timeStamp() + "Success sell cut loss"
            if self.debug:
                print(message)
            return message

    def toredabiRoutine(self):
        self.getStatus()
        if self.status:
            ret = ""
            ret += self.getHold() + "\n"
            ret += self.getOrder() + "\n"
            ret += self.getSuggested() + "\n"
            ret += self.buySuggestedStock() + "\n"
            ret += self.sellProfitable() + "\n"
            ret += self.sellCutLoss() + "\n"

            message = timeStamp() + "Success routine"
            if self.debug:
                print(message)
            return ret + message
        else:
            message = timeStamp() + "Fail routine: Closed"
            if self.debug:
                print(message)
            return message

    def _getSoupText(self):
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        return soup, text
