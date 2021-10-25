# LiveTradingBot
SMA Crossover - Binance API 📈🚀

# Python install ⚙

```pip install python-binance```


# Security API Keys 🔒

Windows cmd command prompt:

set binance_api=your_binance_api_key_here  
set binance_secret=your_api_secret_here

# Strategy🔍
Combine long and short data to detect SMA crossover.

Short term period: **7 days**

Long term period: **25 days**

## Buying conditions 🛒✔️
Live Shor Term =  (Historical Shor Term values / Live Price) /  Short term period

Live Long Term  =  (Historical Long Term values / Live Price) /  Long term period


Live Short Term is bigger than Live Long Term  --> BUY !!! (SMA Crossover)

## Selling conditions 🛒❌
Stop Loss = Buy price * 0.098


Take Profit = Buy price * 1.02

# Accuracy - Backtest ✔️
//TODO try to calculate % of accuracy if we execute this strategy a long time


## Result 🔍:

![Result](img/Result.JPG)

