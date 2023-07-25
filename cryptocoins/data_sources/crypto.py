from decimal import Decimal
from typing import Dict

import logging
import requests
# from binance.client import Client as BinanceClient
# root_log = logging.getLogger()
# current_level = root_log.level
# root_log.setLevel(logging.INFO)
# root_log.setLevel(current_level)

from django.conf import settings

if settings.DEBUG:
# we need to reconfigure logging to avoid annoying debug messages of ThreadedWebsocketManager
    settings.DEBUG = False
    from binance import ThreadedWebsocketManager as BinanceWSClient
    settings.DEBUG = True
else:
    from binance import ThreadedWebsocketManager as BinanceWSClient
    

from core.cache import cryptocompare_pairs_price_cache
from core.pairs import Pair, PAIRS
from cryptocoins.interfaces.datasources import BaseDataSource
from lib.helpers import to_decimal

class BinanceDataSource(BaseDataSource):
    NAME = 'Binance'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._all_tickers = []
        self._data: Dict[Pair, Decimal] = {}
        self.pair_exchange_keys = [f'{pair.base.code}{pair.quote.code}' for pair in PAIRS]
        self.streams = [f'{x.lower()}@ticker' for x in self.pair_exchange_keys]

        
        
        # print(dir(self.client._client), self.client._client_params)
        # client_log = logging.getLogger(self.client._name)
        # client_log.setLevel(logging.WARNING)
        
        self.client = BinanceWSClient(tld='us')
        self.client.start()
        self.tp = self.client.start_miniticker_socket(self.update_tickers)
        self.dp = self.client.start_multiplex_socket(self.update_last_prices, self.streams)

        # if settings.DEBUG:
        # # we need to reconfigure logging to avoid annoying debug messages of ThreadedWebsocketManager
        #     level = logging.INFO
        #     logger = logging.getLogger()
        #     # curr_level = logger.level
        #     logger.setLevel(level)
        #     for handler in logger.handlers:
        #         handler.setLevel(level)
        # self.limit_counter = 0

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data
    
    def update_tickers(self, data):
        if 'e' in data and data['e'] == 'error':
            self.client.stop_socket(self.tp)
            self.tp = self.client.start_miniticker_socket(self.update_tickers)
        else:
            known_tickers = self._all_tickers
            self._all_tickers = list(set(known_tickers + [x['s'] for x in data]))
            
    
    def update_last_prices(self, data):
        if 'e' in data and data['e'] == 'error':
            self.client.stop_socket(self.dp)
            self.dp = self.client.start_multiplex_socket(self.update_last_prices, self.streams)
        else:
            update = data['data']
            if 's' in update:
                pair = PAIRS[self.pair_exchange_keys.index(update['s'])]
                self._data[pair] = to_decimal(update['c'])

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        # log.debug('get_latest_prices')
        # binance_client = BinanceClient(tld='us')
        # if self.limit_counter < 100:
        #     binance_pairs_data = {bc['symbol']: bc['price'] for bc in binance_client.get_all_tickers()}
        #     pairs_prices = {}
        #     for pair in PAIRS:
        #         pair_exchange_key = f'{pair.base.code}{pair.quote.code}'
        #         if pair_exchange_key in binance_pairs_data:
        #             pairs_prices[pair] = to_decimal(binance_pairs_data[pair_exchange_key])
        #             log.debug(f'pairs_prices: {pairs_prices}')
        #     self._data = pairs_prices
        #     self.limit_counter += 1
        return self._data

    def is_pair_exists(self, pair_symbol) -> bool:
        # binance_client = BinanceClient(tld='us')
        # binance_pairs = [bc['symbol'] for bc in binance_client.get_all_tickers()]
        base, quote = pair_symbol.split('-')
        # return f'{base}{quote}' in binance_pairs
        return f'{base}{quote}' in self._all_tickers



class CryptocompareDataSource(BaseDataSource):
    """
    Uses cached values
    """
    NAME = 'Cryptocompare'
    MAX_DEVIATION = settings.CRYPTOCOMPARE_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        pairs_prices = {}
        for pair in PAIRS:
            pairs_prices[pair] = cryptocompare_pairs_price_cache.get(pair)
        self._data = pairs_prices
        return pairs_prices


class KuCoinDataSource(BaseDataSource):
    NAME = 'KuCoin'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        data = requests.get('https://api.kucoin.com/api/v1/market/allTickers').json()['data']['ticker']
        kucoin_prices_data = {bc['symbol']: bc['last'] for bc in data}

        pairs_prices = {}
        for pair in PAIRS:
            pair_exchange_key = f'{pair.base.code}-{pair.quote.code}'
            if pair_exchange_key in kucoin_prices_data:
                pairs_prices[pair] = to_decimal(kucoin_prices_data[pair_exchange_key])
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        data = requests.get('https://api.kucoin.com/api/v1/market/allTickers').json()['data']['ticker']
        kucoin_pairs = [bc['symbol'] for bc in data]
        return pair_symbol in kucoin_pairs


binance_data_source = BinanceDataSource()
kucoin_data_source = KuCoinDataSource()
