from TradeDerPy.TradeDerPy import TradeDerPy
from private import username, password


account = {
    "username": username,
    "password": password,
}
config = {
    "headless": False,
    "debug": True,
    "driverPath": "./chromedriver",
}

# login
td = TradeDerPy(account, config)
td.open()
td.login()

# get data
td.getStatus()
td.showStatus()
td.getHold()
td.showHold()
td.getOrder()
td.showOrder()
td.getSuggested()
td.showSuggested()

# buy
td.getSuggested()
if len(td.suggested) != 0:
    name = td.suggested["name"][0]
    maximum = 1000000
    td.buy(name, maximum)

# sell
td.getHold()
if len(td.hold) != 0:
    name = td.hold["name"][0]
    url = td.hold["sellURL"][0]
    quantity = td.hold["quantity"][0]
    td.sell(name, url, quantity)

# finish
td.close()
