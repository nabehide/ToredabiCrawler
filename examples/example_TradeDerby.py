from ToredabiCrawler.TradeDerby import TradeDerby
from private import username, password


account = {"username": username, "password": password}
config = {"headless": False, "debug": True}

td = TradeDerby(account, config)
td.login()

td.updatePositionHold()
print("Current hold")
print(td.hold["name"])

td.buySuggestedStock()
td.sellRandom()

td.updateOrder()
print("Ordering", td.orderURL.keys())

td.close()
