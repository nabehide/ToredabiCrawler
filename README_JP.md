# TradeDerPy
- トレダビという株売買シミュレーションサイトのスクレイピング用モジュールをPython3で作成しました。
- selenium, beautifulsoup4を使っています。
- 今のところChromeに対応しています。headlessもできます。
- 使用に関しては自己責任でお願いします。
- ソースコードは[TradeDerPy](https://github.com/nabehide/TradeDerPy)です。

## 準備
### (Headless) Chrome
- [chrome](https://www.google.co.jp/chrome/browser/desktop/index.html)をインストール、[chrome driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)をダウンロードして解凍しましょう。

### TradeDerPy
- pipを使うか、

```
$ pip install TradeDerPy
```

- git cloneなどでモジュールをインストールしてください。
```
$ git clone https://github.com/nabehide/TradeDerPy.git
$ cd TradeDerPy
$ pip install -r requirements.txt
$ python setup.py install
```

## 使い方
### importなど
- まずimportとログインに必要な設定などを書きます。

``` examples.py
from TradeDerPy import TradeDerPy

# ログインしたいアカウントのユーザーネームとパスワード
account = {"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}

config = {
    "headless": True, # headlessで実行したい時はTrue
    "debug": True,  # 実行結果などを出力したい場合はTrue
    "driverPath": "./chromedriver",  # chromedriverのパス
}
```

### login
- アカウント情報などを渡して、ブラウザを開いてログインします。
```
td = TradeDerPy(account, config)
td.open()  # ブラウザを開く
td.login()  # ログイン
```

### データ取得・表示
- 情報を取得・表示できます。
```
td.getStatus()  # 現在の取引状況（取引できる状態か）を取得
td.showStatus()  # 取引状況を表示

td.getHold()  # 現在持っている株の情報を取得
td.showHold()  # 持っている株の情報を表示

td.getOrder()  # 現在の取引の待ち状況を取得
td.showOrder()  # 取引の待ち状況を表示

td.getSuggested()  # おすすめな株を取得（Starが2のもの）
td.showSuggested()  # おすすめな株を表示
```

### 買う
- おすすめな株の情報を取得して、その中から選んで買います。
```
td.getSuggested()  # おすすめな株を取得（Starが2のもの）
if len(td.suggested) != 0:  # おすすめな株があれば買う
    idx = 0  # おすすめな株リストの1番目を選択
    name = td.suggested["name"][idx]  # 株の番号（****Tの****の部分）
    maximum = 1000000  # 購入金額の最大値（この金額以内で買えるだけ買う）
    td.buy(name, maximum)
```

### 売る
- 現在持っている株の情報を取得して、その中から選んで売ります。
```
td.getHold()  # 現在持っている株の情報を取得
if len(td.hold) != 0:  # 現在何かしらの株を持っていれば売る
    idx = 0  # 現在持っている株リストの1番目を選択
    name = td.hold["name"][0]  # 株の名前
    url = td.hold["sellURL"][0]  # 売却ページのURL
    td.sell(name, url)
```

### 終了
- close()でブラウザを閉じます
```
td.close()
```

### Examples
- [リポジトリのexamples](https://github.com/nabehide/TradeDerPy/tree/master/examples)に簡単なコードがあるので、こちらも参考にしてください。
