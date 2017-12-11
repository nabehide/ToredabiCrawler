[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintainability](https://api.codeclimate.com/v1/badges/bcca31b9a77a97f213d9/maintainability)](https://codeclimate.com/github/nabehide/TradeDerPy/maintainability)

# TradeDerPy
Crawl in TradeDerby using (Headless) Chrome.

## Prepare
### (Headless) Chrome
- Install [Chrome](https://www.google.co.jp/chrome/browser/desktop/index.html)
- Download chromedriver from [download page](https://sites.google.com/a/chromium.org/chromedriver/downloads).

### TradeDerPy
- You can use pip.

```
$ pip install TradeDerPy
```

- Or git clone.
```
$ git clone https://github.com/nabehide/TradeDerPy.git
$ cd TradeDerPy
$ pip install -r requirements.txt
$ python setup.py install
```

## How to use
### import

```
import TradeDerPy.TradeDerPy import TradeDerPy

account = {"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}

config = {
    "headless": True,
    "debug": True,
    "driverPath": "./chromedriver",
}
```

### Login
```
td = TradeDerPy(account, config)
td.open()
td.login()
```

### Get / Show information
```
td.getStatus()
td.showStatus()

td.getHold()
td.showHold()

td.getOrder()
td.showOrder()

td.getSuggested()
td.showSuggested()
```

### Buy
```
td.getSuggested()
if len(td.suggested) != 0:
    idx = 0
    name = td.suggested["name"][idx]
    maximum = 1000000
    td.buy(name, maximum)
```

### Sell
```
td.getHold()
if len(td.hold) != 0:
    idx = 0
    name = td.hold["name"][0]
    url = td.hold["sellURL"][0]
    td.sell(name, url)
```

### End
```
td.close()
```

### Examples
- Please refer to [examples](https://github.com/nabehide/TradeDerPy/tree/master/examples).
