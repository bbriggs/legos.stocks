# Legobot Stocks

[![Travis](https://img.shields.io/travis/Legobot/legos.stocks.svg)]() [![PyPI](https://img.shields.io/pypi/pyversions/legos.stocks.svg)]() [![PyPI](https://img.shields.io/pypi/v/legos.stocks.svg)]()

[![PyPI](https://img.shields.io/pypi/wheel/legos.stocks.svg)]() [![PyPI](https://img.shields.io/pypi/l/legos.stocks.svg)]() [![PyPI](https://img.shields.io/pypi/status/legos.stocks.svg)]()

## Usage

The `stocks` package actually contains two legos: `stocks`, which reads ticker symbols, and `cryptocurrency` which looks up cryptocurrency symbols such as BTC.

The usage for both is similar:

`!stocks APPL`
`!crypto BTC`

## Installation

`pip3 install legos.stocks`

This is a Lego designed for use with [Legobot](https://github.com/bbriggs/Legobot), so you'll get Legobot along with this. To deploy it, import the package and add it to the active legos like so:

```python
# This is the legobot stuff
from Legobot import Lego
# This is your lego
from legos.stocks import Stocks
from legos.stocks import Cryptocurrency

# Legobot stuff here
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add your lego
baseplate_proxy.add_child(Stocks)
baseplate_proxy.add_child(Cryptocurrency)
```

## Tweaking

While you can use this one as-is, you could also add a localized version to your Legobot deployment by grabbing [stocks.py](legos/stocks.py) or [cryptocurrency.py](legos/cryptocurrency.py) and deploying is as a local module. [Example of a Legobot instance with local modules](https://github.com/voxpupuli/thevoxfox/)

## Contributing

As always, pull requests are welcome.
