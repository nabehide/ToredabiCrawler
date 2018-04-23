# -*- coding: utf-8 -*-

import re
import random
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium.common.exceptions as EC
from selenium.webdriver.chrome.options import Options

from TradeDerPy.parameter import (
    mainURL, loginPath, PositionHoldPath, orderPath,
    dashboardsPath,
    defaultSearchVariables,
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
        self.columnsSuggested = [
            "num", "name", "URL", "rateDay", "rateHold", "sellURL", "quantity",
            "star", "safety", "unitPrice",
        ]
        self.hold = []
        self.suggested = []
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

    def search(self, variables):
        queryTraded = "&traded=true" if variables["traded"] else ""
        queryCommand = "&command=" + variables["command"]
        queryIdx1 = "&idx1=true" if variables["idx1"] else "&idx1=" \
            if variables["idx1"] is None else "&idx1=false"
        queryMinUnitPrice = "&lospl=" if variables["minUnitPrice"] is None \
            else "&lospl=" + str(variables["minUnitPrice"])
        queryMaxUnitPrice = "&losph=" if variables["maxUnitPrice"] is None \
            else "&losph=" + str(variables["maxUnitPrice"])
        queryMinmkcp = "&mkcpl=" if variables["minmkcp"] is None \
            else "&mkcpl=" + str(variables["minmkcp"])
        queryMaxmkcp = "&mkcph=" if variables["maxmkcp"] is None \
            else "&mkcph=" + str(variables["maxmkcp"])
        queryMinPBR = "&cpbrl=" if variables["minPBR"] is None \
            else "&cpbrl=" + str(variables["minPBR"])
        queryMaxPBR = "&cpbrh=" if variables["maxPBR"] is None \
            else "&cpbrh=" + str(variables["maxPBR"])
        queryMinPER = "&cperl=" if variables["minPER"] is None \
            else "&cperl=" + str(variables["minPER"])
        queryMaxPER = "&cperh=" if variables["maxPER"] is None \
            else "&cperh=" + str(variables["maxPER"])
        querySuggest = "" if variables["suggest"] == 0 \
            else "&suggest=" + str(variables["suggest"])
        querySafery = "&safety=true" if variables["safery"] else ""

        searchPath = (
            "/td/quotes/query?query=&exch=&jsec=" + queryTraded +
            queryCommand + queryIdx1 + queryMinUnitPrice +
            queryMaxUnitPrice + queryMinmkcp + queryMaxmkcp + queryMinPBR +
            queryMaxPBR + queryMinPER + queryMaxPER +
            querySuggest + querySafery + "&sort_rank1=quote_code+asc")
        self.driver.get(mainURL + searchPath)

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

        return stock

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
        print("name", name)
        print("unit", unit)
        print("minimumPrice", minimumPrice)
        print("maximum", maximum)
        print("purchase", purchase)
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
        self.hold = []

        self.driver.get(mainURL + PositionHoldPath)
        soup, text = self._getSoupText()
        for tag in soup.select(".stockData"):
            try:
                tagQuote = tag.find(href=re.compile("/td/quotes"))
                if tagQuote is not None:
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
                        tag.select(".omamoriSafety")) != 0 else False
                    unitPrice = tagALR[2].text
                    self.hold.append([
                        stockName, url, rateDay, rateOwn, sellURL, quantity,
                        star, safety, unitPrice])
            except (IndexError, AttributeError):
                pass

        message = timeStamp() + "Success get Hold"
        if self.debug:
            print(message)
        return message

    def showHold(self):
        for i in range(len(self.hold)):
            for j in range(len(self.hold[i])):
                print(self.hold[i][j], " ", end="")
            print()

    def getSuggested(self):
        self.suggested = []

        variables = defaultSearchVariables
        variables["suggest"] = 2
        variables["safety"] = True
        stock = self.search(variables)

        excludeList = list(range(1700)) + list(range(2030, 2070)) + \
            list(range(2050, 2517))

        key = [i for i in list(stock.keys()) if i.isdigit() and int(
               i) not in excludeList]
        extractedKey = []
        for i in key:
            flag = True
            for j in list(self.orderURL):
                if i in j:
                    flag = False
                    break
            nameList = [self.hold[i][
                self.columnsHold.index("name")] for i in range(len(self.hold))]
            for j in nameList:
                if flag and i in j:
                    flag = False
                    break
            if flag:
                extractedKey.append(i)
        for i in extractedKey:
            self.suggested.append([i, stock[i]])

        message = timeStamp() + "Success get suggested"
        if self.debug:
            print(message)
        return message

    def showSuggested(self):
        for i in range(len(self.suggested)):
            print(self.suggested[i])

    def buySuggestedStock(self):
        if len(self.suggested) == 0:
            message = timeStamp() + "Fail buy suggested stock: Not found"
            if self.debug:
                print(message)
            return message

        ret = ""
        for idx in range(len(self.suggested)):
            ret += self.buy(
                self.suggested[idx][self.columnsSuggested.index("name")],
                self.asset * 0.05
            ) + "\n"
            # if "Fail" in ret:
            #     break

        message = ret + timeStamp() + "Success buy suggested stock"
        if self.debug:
            print(message)
        return message

    def sellRandom(self):
        if len(self.hold) == 0:
            print("There is no stock")
            return False

        idx = random.randint(0, len(self.hold) - 1)
        name = self.hold[idx][self.columnsHold.index("name")]
        url = self.hold[idx][self.columnsHold.index("sellURL")]
        quantity = self.hold[idx][self.columnsHold.index("quantity")]
        ret = self.sell(name, url, quantity) + "\n"

        message = ret + timeStamp() + "Success sell random"
        if self.debug:
            print(message)
        return message

    def sellCutLoss(self):
        candidate = []
        for i in range(len(self.hold)):
            if self.hold[i][self.columnsHold.index("star")] <= 0:
                candidate.append(self.hold[i])

        if len(candidate) == 0:
            message = timeStamp() + "Fail sell CutLoss: No candidate"
            if self.debug:
                print(message)
            return message
        else:
            ret = ""
            for i in range(len(candidate)):
                name = candidate[i][self.columnsHold.index("name")]
                url = candidate[i][self.columnsHold.index("url")]
                quantity = candidate[i][self.columnsHold.index("quantity")]
                ret += self.sell(name, url, quantity) + "\n"

            h = []
            for i in range(len(self.hold)):
                if 0 < self.hold[i][self.columnsHold.index("star")]:
                    h.append(self.hold[i])
            self.hold = h

            message = ret + timeStamp() + "Success sell cut loss"
            if self.debug:
                print(message)
            return message

    def sellProfitable(self):
        candidate = []
        for i in range(len(self.hold)):
            if self.hold[i][self.columnsHold.index("star")] <= 1 and \
                    10 < self.hold[i][self.columnsHold.index("rateHold")]:
                candidate.append(self.hold[i])

        if len(candidate) == 0:
            message = timeStamp() + "Fail sell profirable: No candidate"
            if self.debug:
                print(message)
            return message
        else:
            ret = ""
            for i in range(len(candidate)):
                name = candidate[i][self.columnsHold.index("name")]
                url = candidate[i][self.columnsHold.index("url")]
                quantity = candidate[i][self.columnsHold.index("quantity")]
                ret += self.sell(name, url, quantity) + "\n"

            h = []
            for i in range(len(self.hold)):
                if 0 < self.hold[i][self.columnsHold.index("star")]:
                    h.append(self.hold[i])

            message = ret + timeStamp() + "Success sell cut loss"
            if self.debug:
                print(message)
            return message

    def routineDay(self):
        try:
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
        except EC.TimeoutException as e:
                return e

    def _getSoupText(self):
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        return soup, text
