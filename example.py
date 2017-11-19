from core.TradeDerby import TradeDerby
from private import username, password


td = TradeDerby(username, password, headless=True, debug=True)
td.login()

td.getSuggestedStock()

td.updatePositionHold()
print("Current hold")
print(td.hold["name"])

td.updateOrder()
print("Ordering", td.orderURL.keys())

td.close()
