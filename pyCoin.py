import requests
from tabulate import tabulate


class Crypto(object):
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.symbol = data["symbol"]
        self.website_slug = data["website_slug"]
        self.currencies = None

    def get_ticker(self, convert="USD"):
        url = f"https://api.coinmarketcap.com/v2/ticker/{self.id}/?convert={convert}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            # Add the ticker value from the JSON
            ticker = r.json()["data"]
            self.rank = ticker["rank"]
            data = {"price": ticker["quotes"][convert]["price"],
                    "volume_24h": ticker["quotes"][convert]["volume_24h"],
                    "percent_change_24h": ticker["quotes"][convert]["percent_change_24h"],
                    "percent_change_7d": ticker["quotes"][convert]["percent_change_7d"]}
            if self.currencies:
                self.currencies[convert] = data
            else:
                self.currencies = {convert: data}
        else:
            raise ConnectionError(f"{url} [{r.status_code}]")

    def set_ticker(self, ticker, convert):
        self.rank = ticker["rank"]
        data = {"price": ticker["quotes"][convert]["price"],
                "volume_24h": ticker["quotes"][convert]["volume_24h"],
                "percent_change_24h": ticker["quotes"][convert]["percent_change_24h"],
                "percent_change_7d": ticker["quotes"][convert]["percent_change_7d"]}
        if self.currencies:
            self.currencies[convert] = data
        else:
            self.currencies = {convert: data}


class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def bold(text):
    return bcolors.BOLD + str(text) + bcolors.ENDC


def color(text, color):
    colors = {"p": bcolors.PINK, "b": bcolors.BLUE, "g": bcolors.GREEN, "y": bcolors.YELLOW, "r": bcolors.RED}
    return colors[color] + str(text) + bcolors.ENDC


def color_percent(value):
    if value < 0:
        return color(value / 100, "r")
    else:
        return color(value / 100, "g")


def load_cmc_ids():
    # Get the JSON file from CMC API : https://api.coinmarketcap.com/v2/listings/
    url = "https://api.coinmarketcap.com/v2/listings/"
    r = requests.get(url, timeout=10)

    if r.status_code == 200:
        # Parse the JSON into a dict of Crypto objects
        return {data["symbol"]: Crypto(data) for data in r.json()["data"]}
    else:
        raise ConnectionError(f"{url} [{r.status_code}]")


def get_top_10(cryptos, convert="USD"):
    selected = set()
    for conv in convert.split(","):
        url = f"https://api.coinmarketcap.com/v2/ticker/?limit=10&convert={conv}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            # Parse the JSON and update the Crypto objects
            data = r.json()['data']
            for key in data:
                cryptos[data[key]["symbol"]].set_ticker(data[key], conv)
                selected.add(cryptos[data[key]["symbol"]])
        else:
            raise ConnectionError(f"{url} [{r.status_code}]")

    # Sort the result by rank
    return sorted(list(selected), key=lambda x: x.rank, reverse=False)


def get_symbols(cryptos, symbols, convert="USD"):
    selected = set()
    for symbol in symbols.split(","):
        if symbol in cryptos:
            for conv in convert.split(","):
                cryptos[symbol].get_ticker(conv)
                selected.add(cryptos[symbol])

        else:
            print(color(f"Couldn't find '{symbol}' on CoinMarketCap.com", 'p'))

    # Sort the result by rank
    return sorted(list(selected), key=lambda x: x.rank, reverse=False)


def print_selection_onetab(selection):
    # Generate a list of lists containing the data to print
    to_print = []
    for item in selection:
        prices = [item.currencies[c]['price'] for c in item.currencies]
        volumes = [item.currencies[c]['volume_24h'] for c in item.currencies]
        percentages_24h = [color_percent(item.currencies[c]['percent_change_24h']) for c in item.currencies]
        percentages_7d = [color_percent(item.currencies[c]['percent_change_7d']) for c in item.currencies]
        data = [bold(item.rank), item.symbol, item.name] + prices + percentages_24h + percentages_7d + volumes
        to_print.append(data)

    currencies = selection[0].currencies
    headers = ["Rank", "Symbol", "Name"] + [f"Price ({c})" for c in currencies] + \
              [f"24h-Change ({c})" for c in currencies] + [f"7d-Change ({c})" for c in currencies] + \
              [f"24h-Volume ({c})" for c in currencies]
    headers = [bold(h) for h in headers]

    floatfmt = ["", "", ""] + [".8f" if c == 'BTC' else ".4f" for c in currencies] + \
               [".2%" for _ in range(len(currencies) * 2)] + [".4f" if c == 'BTC' else ",.0f" for c in currencies]

    print(tabulate(to_print, headers=headers, floatfmt=floatfmt))


def print_selection_multitab(selection):
    for currency in selection[0].currencies:
        # Generate a list of lists containing the data to print
        to_print = []
        for item in selection:
            price = item.currencies[currency]['price']
            volume = item.currencies[currency]['volume_24h']
            percentage_24h = color_percent(item.currencies[currency]['percent_change_24h'])
            percentage_7d = color_percent(item.currencies[currency]['percent_change_7d'])
            data = [bold(item.rank), item.symbol, item.name, price, percentage_24h, percentage_7d, volume]
            to_print.append(data)

        headers = ["Rank", "Symbol", "Name", f"Price ({currency})", f"24h-Change ({currency})",
                   f"7d-Change ({currency})", f"24h-Volume ({currency})"]
        headers = [bold(h) for h in headers]

        floatfmt = ["", "", "", f"{'.8f' if currency == 'BTC' else '.4f'}", ".2%",
                    ".2%", f"{'.4f' if currency == 'BTC' else ',.0f'}"]

        print(color(bold("\n" + currency), "y"))
        print(tabulate(to_print, headers=headers, floatfmt=floatfmt))


def main(currency, symbols):
    # Load the crypto ids from CMC
    cryptos = load_cmc_ids()

    # Get the tickers of the top 10 cryptos
    if symbols:
        selection = get_symbols(cryptos, symbols, currency)
    else:
        selection = get_top_10(cryptos, currency)

    # Print the selection
    # print_selection_onetab(selection)
    print_selection_multitab(selection)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Displays cryptocurrencies data from CMC in the terminal')

    parser.add_argument('--curr', default='USD', type=str,
                        help='Currency used for the price and volume')
    parser.add_argument('--crypt', default=None, type=str,
                        help='Symbols of the cryptocurrencies to display. Default top 10.')

    args = parser.parse_args()
    # TODO: check if the currency is supported by CMC, if not use USD
    # TODO: add multiple currencies support (ex: USD,EUR,BCT)
    # TODO: add the possibility to sort by rank (default), value, volume, 24h pourcentage or keep the args order

    if args.crypt:
        main(args.curr.upper(), args.crypt.upper().replace(" ", ""))
    else:
        main(args.curr.upper(), None)
