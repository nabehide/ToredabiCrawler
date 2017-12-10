from TradeDerpy.TradeDerPy import TradeDerPy
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

td = TradeDerPy(account, config)
td.open()
td.login()

td.close()
