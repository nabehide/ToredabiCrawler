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
git clone https://github.com/nabehide/TradeDerPy.git
cd TradeDerPy
python setup.py install
```

## 使い方
### importなど
- まずimportとログインに必要な設定などを書きます。

``` examples.py
import TradeDerPy.TradeDerPy import TradeDerPy

# ログインしたいアカウントのユーザーネームとパスワード
account = {"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}

config = {
    "headless": True, # headlessで実行したい時はTrue
    "debug": False,  # 実行結果などを出力したい場合はTrue
}
```

### login
- アカウント情報などを渡して、ブラウザを開いてログインします。
```
td = TradeDerPy(account, config)
td.open()  # ブラウザを開く
td.login()  # ログイン
```

### 売り買い
```
td.buy(name, url, maximum)
td.sell(name, url)
```

### データ取得・表示
- 情報を取得・表示できます。
```
td.getStatus()  # 現在の取引状況（取引できる状態か）を取得
td.showStatus()  # 取引状況を取得

td.getHold()  # 現在持っている株の情報を取得
td.showHold()  # 持っている株の情報を表示

td.getOrder()  # 現在の取引の待ち状況を取得
td.showOrder()  # 取引の待ち状況を表示
```

### 終了
- close()でブラウザを閉じます
```
td.close()
```

### Examples
- [リポジトリのexamples](https://github.com/nabehide/TradeDerPy/examples)に簡単なコードがあるので、こちらも参考にしてください。
