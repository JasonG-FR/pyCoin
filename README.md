# pyCoin
A python script (CLI) for displaying crypto currencies data from CMC in the terminal

![logo_pyCoin](logo_pyCoin_200px.png)

Logo attribution: [Snake](https://thenounproject.com/vishal.marotkar/uploads/?i=316335) by **V I S H A L** & [crypto currency](https://thenounproject.com/term/crypto-currency/1372103) by **Iconika** from the [Noun Project](https://thenounproject.com)

## Help
`$ python pyCoin.py -h`

## Showing the top10 crypto currencies
### Basic usage
```
$ python pyCoin.py

> USD
  Rank  Symbol    Name            Price (USD)    24h-Change (USD)    7d-Change (USD)    24h-Volume (USD)
------  --------  ------------  -------------  ------------------  -----------------  ------------------
     1  BTC       Bitcoin           6422.3400              -5.44%             -2.14%       4,198,030,000
     2  ETH       Ethereum           443.2360              -8.07%             -4.90%       1,836,870,000
     3  XRP       XRP                  0.4508              -5.65%             -7.96%         232,477,000
     4  BCH       Bitcoin Cash       702.0190              -5.90%             -8.11%         397,593,000
     5  EOS       EOS                  7.5138              -8.40%            -15.23%         785,788,000
     6  LTC       Litecoin            78.3568              -4.18%             -8.89%         334,470,000
     7  XLM       Stellar              0.1962              -6.62%             -5.72%          38,414,200
     8  ADA       Cardano              0.1327              -7.07%            -13.14%          65,454,700
     9  MIOTA     IOTA                 0.9920              -6.92%            -13.65%          51,892,900
    10  USDT      Tether               1.0001              -0.67%              0.07%       3,108,730,000

Source: https://www.coinmarketcap.com - 2018-07-10 23:32:53
```

### Currencies
Available currencies:

Fiats: 

USD, AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR


Cryptos: 

BTC, ETH, XRP, LTC, BCH

#### Using another currency
```
$ python pyCoin.py --curr EUR

> EUR
  Rank  Symbol    Name            Price (EUR)    24h-Change (EUR)    7d-Change (EUR)    24h-Volume (EUR)
------  --------  ------------  -------------  ------------------  -----------------  ------------------
     1  BTC       Bitcoin           5463.1473              -5.61%             -2.29%       3,576,168,479
     2  ETH       Ethereum           377.1409              -8.23%             -5.02%       1,566,580,302
     3  XRP       XRP                  0.3836              -5.86%             -8.05%         198,211,059
     4  BCH       Bitcoin Cash       596.6292              -6.14%             -8.34%         339,011,523
     5  EOS       EOS                  6.3553              -9.05%            -15.84%         669,170,388
     6  LTC       Litecoin            66.0718              -5.20%             -9.81%         284,385,334
     7  XLM       Stellar              0.1675              -6.43%             -5.49%          32,623,837
     8  ADA       Cardano              0.1124              -7.63%            -13.61%          55,799,441
     9  MIOTA     IOTA                 0.8428              -7.15%            -13.86%          44,307,606
    10  USDT      Tether               0.8531              -0.57%              0.15%       2,651,476,153

Source: https://www.coinmarketcap.com - 2018-07-10 23:45:56
```

#### Using multiple currencies
```
$ python pyCoin.py --curr USD,EUR

> USD
  Rank  Symbol    Name            Price (USD)    24h-Change (USD)    7d-Change (USD)    24h-Volume (USD)
------  --------  ------------  -------------  ------------------  -----------------  ------------------
     1  BTC       Bitcoin           6422.3400              -5.44%             -2.14%       4,198,030,000
     2  ETH       Ethereum           443.2360              -8.07%             -4.90%       1,836,870,000
     3  XRP       XRP                  0.4508              -5.65%             -7.96%         232,477,000
     4  BCH       Bitcoin Cash       702.0190              -5.90%             -8.11%         397,593,000
     5  EOS       EOS                  7.5138              -8.40%            -15.23%         785,788,000
     6  LTC       Litecoin            78.3568              -4.18%             -8.89%         334,470,000
     7  XLM       Stellar              0.1962              -6.62%             -5.72%          38,414,200
     8  ADA       Cardano              0.1327              -7.07%            -13.14%          65,454,700
     9  MIOTA     IOTA                 0.9920              -6.92%            -13.65%          51,892,900
    10  USDT      Tether               1.0001              -0.67%              0.07%       3,108,730,000

> EUR
  Rank  Symbol    Name            Price (EUR)    24h-Change (EUR)    7d-Change (EUR)    24h-Volume (EUR)
------  --------  ------------  -------------  ------------------  -----------------  ------------------
     1  BTC       Bitcoin           5463.1473              -5.61%             -2.29%       3,576,168,479
     2  ETH       Ethereum           377.1409              -8.23%             -5.02%       1,566,580,302
     3  XRP       XRP                  0.3836              -5.86%             -8.05%         198,211,059
     4  BCH       Bitcoin Cash       596.6292              -6.14%             -8.34%         339,011,523
     5  EOS       EOS                  6.3553              -9.05%            -15.84%         669,170,388
     6  LTC       Litecoin            66.0718              -5.20%             -9.81%         284,385,334
     7  XLM       Stellar              0.1675              -6.43%             -5.49%          32,623,837
     8  ADA       Cardano              0.1124              -7.63%            -13.61%          55,799,441
     9  MIOTA     IOTA                 0.8428              -7.15%            -13.86%          44,307,606
    10  USDT      Tether               0.8531              -0.57%              0.15%       2,651,476,153

Source: https://www.coinmarketcap.com - 2018-07-10 23:46:24
```

### Sorting
#### Rank (default)
Descending: `$ python pyCoin.py --sort rank`

Ascending: `$ python pyCoin.py --sort rank-`

#### Price
Descending: `$ python pyCoin.py --sort price`

Ascending: `$ python pyCoin.py --sort price-`

#### 24h-change
Descending: `$ python pyCoin.py --sort change_24h`

Ascending: `$ python pyCoin.py --sort change_24h-`

#### 7d-change
Descending: `$ python pyCoin.py --sort change_7d`

Ascending: `$ python pyCoin.py --sort change_7d-`

#### Volume
Descending: `$ python pyCoin.py --sort volume`

Ascending: `$ python pyCoin.py --sort volume-`


## Showing custom crypto currencies
```
$ python pyCoin.py --crypto BTC,DOGE,MIOTA,GRLC,VTC,LET,NANO

> USD
  Rank  Symbol    Name         Price (USD)    24h-Change (USD)    7d-Change (USD)    24h-Volume (USD)
------  --------  ---------  -------------  ------------------  -----------------  ------------------
     1  BTC       Bitcoin        6398.3000              -5.78%             -2.46%       4,191,200,000
     9  MIOTA     IOTA              0.9874              -7.25%            -13.97%          51,805,400
    41  NANO      Nano              2.3807              -9.44%             -8.24%           5,349,300
    44  DOGE      Dogecoin          0.0024              -8.03%             -9.14%           6,413,170
   168  VTC       Vertcoin          0.9496              -8.73%             -1.43%             451,198
   337  LET       LinkEye           0.0255             -15.55%            -36.43%           1,285,090
   982  GRLC      Garlicoin         0.0137              -8.90%             -9.73%               3,187

Source: https://www.coinmarketcap.com - 2018-07-10 23:52:32
```
