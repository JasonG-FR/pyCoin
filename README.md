![logo_pyCoin](img/logo_pyCoin_blink.gif)

Logo attribution: [Snake](https://thenounproject.com/vishal.marotkar/uploads/?i=316335) by **V I S H A L** & [crypto currency](https://thenounproject.com/term/crypto-currency/1372103) by **Iconika** from the [Noun Project](https://thenounproject.com)

## Help
```bash
$ python pyCoin.py -h
```

## Showing the top10 crypto currencies
### Basic usage
```bash
$ python pyCoin.py
```
![basic usage image](img/term_1.png)

### Currencies
Available currencies:

**Fiats:**

USD, AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR


**Cryptos:**

BTC, ETH, XRP, LTC, BCH

#### Using another currency
```bash
$ python pyCoin.py --curr EUR
```
![another currency image](img/term_2.png)

#### Using multiple currencies
```bash
$ python pyCoin.py --curr USD,EUR
```
![multiple currencies image](img/term_3.png)

### Sorting
#### Rank (default)
Descending: 
```bash
$ python pyCoin.py --sort rank
```

Ascending: 
```bash
$ python pyCoin.py --sort rank-
```

#### Price
Descending: 
```bash
$ python pyCoin.py --sort price
```

Ascending: 
```bash
$ python pyCoin.py --sort price-
```

#### 24h-change
Descending: 
```bash
$ python pyCoin.py --sort change_24h
```

Ascending: 
```bash
$ python pyCoin.py --sort change_24h-
```

#### 7d-change
Descending: 
```bash
$ python pyCoin.py --sort change_7d
```

Ascending: 
```bash
$ python pyCoin.py --sort change_7d-
```

#### Volume
Descending: 
```bash
$ python pyCoin.py --sort volume
```

Ascending: 
```bash
$ python pyCoin.py --sort volume-
```


## Showing custom crypto currencies
```bash
$ python pyCoin.py --crypto BTC,DOGE,MIOTA,GRLC,VTC,LET,NANO
```
![custom crypto image](img/term_4.png)
