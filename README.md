[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintainability](https://api.codeclimate.com/v1/badges/bcca31b9a77a97f213d9/maintainability)](https://codeclimate.com/github/nabehide/toredabiCrawler/maintainability)

# ToredabiCrawler
Crawl in TradeDerby using (Headless) Chrome.

## How to use
### Requirements
- Install dependent modules.

```
pip install -r requirements.txt
```

### Prepare account information
- Download chromedriver from [download page](https://sites.google.com/a/chromium.org/chromedriver/downloads).
- Make "private.py" as follows and put it into "examples" folder.

```private.py
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
```

### Crawl in TradeDerby
- Please refer to "example_TradeDerby.py".
