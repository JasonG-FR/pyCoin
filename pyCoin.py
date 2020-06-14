import requests
import threading

from tabulate import tabulate
from datetime import datetime
from time import sleep


class Thread(threading.Thread):
    def __init__(self, url, cryptos, currencies, key):
        threading.Thread.__init__(self, target=update_ticker, 
                                  args=(url, cryptos, currencies, key))
        self.start()


class Crypto(object):
    def __init__(self, data: dict) -> None:
        self.id = data["id"]
        self.name = data["name"]
        self.symbol = data["symbol"].upper()
        self.website_slug = None
        self.currencies = None

    def set_ticker(self, ticker: dict, currencies: str) -> None:
        # TODO: Add price change 7d for custom cryptos
        self.rank = ticker["market_cap_rank"]
        if "percent_change_7d" in ticker:
            data = ticker

            if self.currencies:
                self.currencies[currencies.upper()] = data
            else:
                self.currencies = {currencies.upper(): data}
        else:
            keys = ["price", "volume_24h", "percent_change_24h",
                    "percent_change_7d"]
            cgecko_keys = ["current_price", "total_volume",
                           "price_change_percentage_24h_in_currency", 
                           "price_change_percentage_7d_in_currency"]

            for currency in currencies.split(","):
                data = {}
                for key, cg_key in zip(keys, cgecko_keys):
                    data[key] = ticker[cg_key][currency.lower()]

                if self.currencies:
                    self.currencies[currency.upper()] = data
                else:
                    self.currencies = {currency.upper(): data}


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


def load_cgecko_cryptos(symbols: str) -> tuple:
    # Get the JSON file from CoinGecko API
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
        return cryptos, "\n".join(errors)

    else:
        raise ConnectionError(f"{url} [{r.status_code}]")


def update_ticker(url: str, cryptos: dict, currencies: str, key: str) -> None:
    key_url = url.format(cryptos[key].id)
    r = requests.get(key_url, timeout=10)

    if r.status_code == 200:
        with lock:
            cryptos[key].set_ticker(r.json()["market_data"], currencies)
    else:
        raise ConnectionError(f"{key_url} [{r.status_code}]")


def update_tickers(cryptos: dict, currencies: str) -> None:
    # Get and set all tickers for each crypto selected
    url = "https://api.coingecko.com/api/v3/coins/{}?" \
          "localization=false&tickers=false&community_data=false" \
          "&developer_data=false&sparkline=false"

    threads = [Thread(url, cryptos, currencies, key) for key in cryptos]
    [t.join() for t in threads]  # Wait until all threads are done to continue


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


def main(currencies, cryptos, sort_value, clear_scr):
    if cryptos:
        # Load the crypto ids from CoinGecko
        update_tickers(cryptos, currencies)
    else:
        # Get the tickers of the top 10 cryptos
        cryptos = get_top_10(currencies)
    
    selection = [cryptos[key] for key in cryptos]

    # Clear the screen if needed
    if clear_scr:
        print(bcolors.CLEAR)

    # Print the selection if any
    if selection:
        print_selection_multitab(selection, sort_value)


lock = threading.Lock()


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

    cryptos = {}
    if args.crypto:
        args.crypto = args.crypto.upper().replace(" ", "")
        cryptos, errors = load_cgecko_cryptos(args.crypto)

        if errors:
            print(errors)

    while True:
        try:
            main(args.curr, cryptos, args.sort, args.delay > 0)
            if args.delay > 0:
                sleep(args.delay)
            else:
                break
        except KeyboardInterrupt:
            break
