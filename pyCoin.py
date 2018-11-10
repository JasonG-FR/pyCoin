import requests
from tabulate import tabulate
from datetime import datetime
from time import sleep


class Crypto(object):
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.symbol = data["symbol"].upper()
        self.website_slug = None
        self.currencies = None

    def set_ticker(self, ticker, conv):
        # TODO: Add price change 7d for custom cryptos
        self.rank = ticker["market_cap_rank"]
        if "percent_change_7d" in ticker:
            data = ticker
        else:
            keys = ["price", "volume_24h", "percent_change_24h",
                    "percent_change_7d"]
            cgecko_keys = ["current_price", "total_volume",
                           "price_change_percentage_24h", ""]

            data = {}
            for key, cg_key in zip(keys, cgecko_keys):
                if key != "percent_change_7d":
                    data[key] = ticker[cg_key]
                else:
                    data[key] = "N/A"

        if self.currencies:
            self.currencies[conv.upper()] = data
        else:
            self.currencies = {conv.upper(): data}


class bcolors:
    WHITE = '\033[97m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CLEAR = '\033[H\033[J'


def bold(text):
    return bcolors.BOLD + str(text) + bcolors.ENDC


def color(text, color):
    colors = {"m": bcolors.MAGENTA, "b": bcolors.BLUE, "y": bcolors.YELLOW,
              "w": bcolors.WHITE, "c": bcolors.CYAN, "r": bcolors.RED,
              "g": bcolors.GREEN}
    return colors[color] + str(text) + bcolors.ENDC


def color_percent(value):
    if value == "N/A":
        return color(value, "r")
    elif value < 0:
        return color(value / 100, "r")
    else:
        return color(value / 100, "g")


def load_cgecko_ids(symbols: str, currencies: str) -> tuple:
    # Get the JSON file from CMC API
    url = "https://api.coingecko.com/api/v3/coins/list"
    r = requests.get(url, timeout=10)

    if r.status_code == 200:
        data = r.json()

        # Parse the JSON into a dict of Crypto objects
        cryptos, errors = {}, []
        cgecko_symbs = [d["symbol"] for d in data]
        for s in symbols.split(","):
            if s.lower() in cgecko_symbs:
                cryptos[s.upper()] = Crypto(data[cgecko_symbs.index(s.lower())])
            else:
                errors.append(color(f"Couldn't find '{s.upper()}' " \
                                    "on CoinGecko.com", 'm'))

        # Get a list of CoinGecko ids for the selected cryptos
        cgecko_ids = [cryptos[key].id for key in cryptos]

        # Get and set all tickers for each currency (fiat) selected
        url = "https://api.coingecko.com/api/v3/coins/markets"
        ids = f"ids={','.join(cgecko_ids)}"

        for curr in currencies.split(","):
            api_curr = f"vs_currency={curr.lower()}"
            r = requests.get(f"{url}?{api_curr}&{ids}", timeout=10)

            if r.status_code == 200:
                tickers = r.json()
                for ticker in tickers:
                    cryptos[ticker['symbol'].upper()].set_ticker(ticker, curr)
            else:
                raise ConnectionError(f"{url}&{curr}&{ids} [{r.status_code}]")

        return cryptos, "\n".join(errors)

    else:
        raise ConnectionError(f"{url} [{r.status_code}]")


def get_top_10(convert: str="USD") -> dict:
    url = "https://api.coingecko.com/api/v3/coins?per_page=10"
    r = requests.get(url, timeout=10)

    if r.status_code == 200:
        # Parse the JSON and update the Crypto objects
        data = r.json()

        cryptos = {d["symbol"].upper(): Crypto(d) for d in data}

        for conv in [c.lower() for c in convert.split(",")]:
            for d in data:
                pc24 = 'price_change_percentage_24h_in_currency'
                pc7 = 'price_change_percentage_7d_in_currency'
                ticker = {
                    "market_cap_rank": d['market_data']['market_cap_rank'],
                    "price": d['market_data']['current_price'][conv],
                    "volume_24h": d['market_data']['total_volume'][conv],
                    "percent_change_24h": d['market_data'][pc24][conv],
                    "percent_change_7d": d['market_data'][pc7][conv]
                }
                cryptos[d["symbol"].upper()].set_ticker(ticker, conv)

    else:
        raise ConnectionError(f"{url} [{r.status_code}]")

    return cryptos


def sort_selection(selection, sort_value, curr):
    cases = {"rank": lambda x: x.rank,
             "price": lambda x: x.currencies[curr]["price"],
             "change_24h": lambda x: x.currencies[curr]["percent_change_24h"],
             "change_7d": lambda x: x.currencies[curr]["percent_change_7d"],
             "volume": lambda x: x.currencies[curr]["volume_24h"]}

    return sorted(selection, key=cases[sort_value.replace("-", "")],
                  reverse="-" not in sort_value)


def print_selection_onetab(selection, sort_value):
    # Generate a list of lists containing the data to print
    to_print = []

    # Sort the selection
    selection = sort_selection(selection, sort_value,
                               selection[0].currencies[0])

    for item in selection:
        currs = item.currencies
        prices = [currs[c]['price'] for c in currs]
        volumes = [currs[c]['volume_24h'] for c in currs]
        percent_24h = [color_percent(currs[c]['percent_change_24h'])
                       for c in currs]
        percent_7d = [color_percent(currs[c]['percent_change_7d'])
                      for c in currs]

        data = [bold(item.rank), item.symbol, item.name]
        data += prices + percent_24h + percent_7d + volumes
        to_print.append(data)

    currs = selection[0].currencies
    headers = ["Rank", "Symbol", "Name"] + [f"Price ({c})" for c in currs] + \
              [f"24h-Change ({c})" for c in currs] + \
              [f"7d-Change ({c})" for c in currs] + \
              [f"24h-Volume ({c})" for c in currs]
    headers = [bold(h) for h in headers]

    floatfmt = [""] * 3 + [".8f" if c == 'BTC' else ".4f" for c in currs] + \
               [".2%" for _ in range(len(currs) * 2)] + \
               [".4f" if c == 'BTC' else ",.0f" for c in currs]

    print(tabulate(to_print, headers=headers, floatfmt=floatfmt))
    # Print the source and timestamp
    print(f"\nSource: {color('https://www.coinmarketcap.com', 'b')} - "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def print_selection_multitab(selection, sort_value):
    for currency in selection[0].currencies:
        # Generate a list of lists containing the data to print
        to_print = []

        # Sort the selection
        selection = sort_selection(selection, sort_value, currency)

        for item in selection:
            currs = item.currencies
            price = currs[currency]['price']
            volume = currs[currency]['volume_24h']
            percent_24h = color_percent(currs[currency]['percent_change_24h'])
            percent_7d = color_percent(currs[currency]['percent_change_7d'])
            data = [bold(item.rank), item.symbol, item.name,
                    price, percent_24h, percent_7d, volume]
            to_print.append(data)

        headers = ["Rank", "Symbol", "Name", f"Price ({currency})",
                   f"24h-Change ({currency})", f"7d-Change ({currency})",
                   f"24h-Volume ({currency})"]
        headers = [bold(h) for h in headers]

        floatfmt = ["", "", "", f"{'.8f' if currency == 'BTC' else '.4f'}",
                    ".2%", ".2%", f"{'.4f' if currency == 'BTC' else ',.0f'}"]

        print(color(bold("\n> " + currency), "y"))
        print(tabulate(to_print, headers=headers, floatfmt=floatfmt))
    # Print the source and timestamp
    print(f"\nSource: {color('https://www.coingecko.com', 'w')} - "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main(currencies, symbols, sort_value, clear_scr):
    if symbols:
        # Load the crypto ids from CoinGecko
        cgecko_cryptos, errors = load_cgecko_ids(args.crypto, currencies)
    else:
        # Get the tickers of the top 10 cryptos
        cgecko_cryptos = get_top_10(currencies)
    
    selection = [cgecko_cryptos[key] for key in cgecko_cryptos]

    # Clear the screen if needed
    if clear_scr:
        print(bcolors.CLEAR)

    # Print the selection if any
    if selection:
        # print_selection_onetab(selection, sort_value)
        print_selection_multitab(selection, sort_value)

    if errors:
        print(errors)


if __name__ == '__main__':
    import argparse

    supported_currencies = ['AED', 'ARS', 'AUD', 'BCH', 'BDT', 'BHD', 'BMD', 
                            'BNB', 'BRL', 'BTC', 'CAD', 'CHF', 'CLP', 'CNY', 
                            'CZK', 'DKK', 'EOS', 'ETH', 'EUR', 'GBP', 'HKD', 
                            'HUF', 'IDR', 'ILS', 'INR', 'JPY', 'KRW', 'KWD', 
                            'LKR', 'LTC', 'MMK', 'MXN', 'MYR', 'NOK', 'NZD', 
                            'PHP', 'PKR', 'PLN', 'RUB', 'SAR', 'SEK', 'SGD', 
                            'THB', 'TRY', 'TWD', 'USD', 'VEF', 'XAG', 'XAU', 
                            'XDR', 'XLM', 'XRP', 'ZAR']
    sorts = ["rank", "rank-", "price", "price-", "change_24h", "change_24h-",
             "change_7d", "change_7d-", "volume", "volume-"]

    parser = argparse.ArgumentParser(description='Displays cryptocurrencies '
                                     'data from CMC in the terminal')
    parser.add_argument('--curr', default='USD', type=str,
                        help='Currency used for the price and volume '
                        '(for more than one, separate them with a comma : '
                        'USD,BTC). Valid currencies: '
                        f'{bold(", ".join(supported_currencies))}, '
                        '(default USD)')
    parser.add_argument('--crypto', default=None, type=str,
                        help='Symbols of the cryptocurrencies to display '
                        '(default top10).')
    parser.add_argument('--sort', default='rank-', type=str, choices=sorts,
                        help='How to sort cryptos (default rank-)')
    parser.add_argument('-d', '--delay', default=0, type=int,
                        help='Autorefresh delay in seconds '
                        '(default Autorefresh off)')

    args = parser.parse_args()

    args.curr = args.curr.upper()
    args.sort = args.sort.lower()

    # Check if the currency is supported by CoinGecko, if not use 'USD'
    for curr in args.curr.split(","):
        if curr not in supported_currencies:
            print(color(f"'{args.curr}' is not a valid currency value, "
                        "using 'USD'", 'm'))
            args.curr = "USD"
            break

    if args.crypto:
        args.crypto = args.crypto.upper().replace(" ", "")

    while True:
        try:
            main(args.curr, args.crypto, args.sort, args.delay > 0)
            if args.delay > 0:
                sleep(args.delay)
            else:
                break
        except KeyboardInterrupt:
            break
