import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from parameter import mainURL, loginPath


class TradeDerby(object):
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password

        options = Options()
        if headless:    options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        self.driver.get(mainURL)

    def login(self):
        loginURL = "https://www.k-zone.co.jp/" + loginPath
        self.driver.get(loginURL)
        self.driver.find_element_by_name("login").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("login_button").click()

    def getSuggestedURL(self):
        searchURL = ("https://www.k-zone.co.jp/td/quotes/query?query=&exch=&"
                     "jsec=&command=spot_buy&idx1=&lospl=&losph=&mkcpl=&"
                     "mkcph=&cpbrl=&cpbrh=&cperl=&cperh=&suggest=2&"
                     "safety=true&sort_rank1=quote_code+asc")
        self.driver.get(searchURL)
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

        return url

    def buy(self, url):
        self.driver.get(url)
        text = self.driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        tag = soup.select(".accordionWrapper1")[0].select(".orderHover1")[0]
        url = mainURL + tag.get("href")

        self.driver.get(url)
        self.driver.find_element_by_class_name("transition").click()
        self.driver.find_elements_by_class_name("transition")[1].click()

    def close(self):
        self.driver.quit()

    def getSuggestedStock(self):
        suggestedURL = self.getSuggestedURL()
        self.buy(suggestedURL)
