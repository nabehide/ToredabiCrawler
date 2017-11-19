from core.TradeDerby import TradeDerby
from private import username, password


td = TradeDerby(username, password)
td.login()

td.getSuggestedStock()
td.updatePositionHold()
print("Current hold", td.hold)

td.close()
