import requests
from tabulate import tabulate


class Crypto(object):
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.symbol = data["symbol"]
        self.website_slug = data["website_slug"]

    def get_ticker(self, convert="USD"):
        url = f"https://api.coinmarketcap.com/v2/ticker/{self.id}/?convert={convert}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            # Add the ticker value from the JSON
            ticker = r.json()["data"]
            self.rank = ticker["rank"]
            self.price = ticker["quotes"][convert]["price"]
            self.percent_change_24h = ticker["quotes"][convert]["percent_change_24h"]
            self.percent_change_7d = ticker["quotes"][convert]["percent_change_7d"]
            self.volume_24h = ticker["quotes"][convert]["volume_24h"]
            self.currency = convert
        else:
            raise ConnectionError(f"{url} [{r.status_code}]")

    def set_ticker(self, ticker, convert):
        self.rank = ticker["rank"]
        self.price = ticker["quotes"][convert]["price"]
        self.percent_change_24h = ticker["quotes"][convert]["percent_change_24h"]
        self.percent_change_7d = ticker["quotes"][convert]["percent_change_7d"]
        self.volume_24h = ticker["quotes"][convert]["volume_24h"]
        self.currency = convert


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
    url = f"https://api.coinmarketcap.com/v2/ticker/?limit=10&convert={convert}"
    r = requests.get(url, timeout=10)

    if r.status_code == 200:
        # Parse the JSON and update the Crypto objects
        data = r.json()['data']
        selected = []
        for key in data:
            cryptos[data[key]["symbol"]].set_ticker(data[key], convert)
            selected.append(cryptos[data[key]["symbol"]])

        return selected
    else:
        raise ConnectionError(f"{url} [{r.status_code}]")


def get_symbols(cryptos, symbols, convert="USD"):
    selected = []
    for symbol in symbols.split(","):
        if symbol in cryptos:
            cryptos[symbol].get_ticker(convert)
            selected.append(cryptos[symbol])

        else:
            print(color(f"Couldn't find '{symbol}' on CoinMarketCap.com", 'y'))

    # Sort the result by rank
    return sorted(selected, key=lambda x: x.rank, reverse=False)


def print_selection(selection):
    # Generate a list of tuple containing the data to print
    to_print = []
    for item in selection:
        data = (bold(item.rank), item.symbol, item.name, item.price, color_percent(item.percent_change_24h),
                color_percent(item.percent_change_7d), item.volume_24h)
        to_print.append(data)

    currency = selection[0].currency
    headers = ["Rank", "Symbol", "Name", f"Price ({currency})", "24h-Change",
               "7d-Change", f"24h-Volume  ({currency})"]
    headers = [bold(h) for h in headers]
    floatfmt = ("", "", "", ".4f", ".2%", ".2%", ",.0f")
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
    print_selection(selection)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Displays cryptocurrencies data from CMC in the terminal')

    parser.add_argument('--curr', default='USD', type=str,
                        help='Currency used for the price and volume')
    parser.add_argument('--crypt', default=None, type=str, 
                        help='Symbols of the cryptocurrencies to display. Default top 10.')

    args = parser.parse_args()
    # TODO: check if the currency is supported by CMC, if not use USD
    # TODO: add the possibility to sort by rank (default), value, volume, 24h pourcentage or keep the args order

    if args.crypt:
        main(args.curr.upper(), args.crypt.upper().replace(" ", ""))
    else:
        main(args.curr.upper(), None)
