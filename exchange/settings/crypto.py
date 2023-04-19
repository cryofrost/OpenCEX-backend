import os

from django.utils import timezone

from exchange.settings import env

CRYPTO_TESTNET = False
FORCE_WALLET_ADDRESS_GENERATE = False

BTC_SAFE_ADDR = env('BTC_SAFE_ADDR')

ETH_SAFE_ADDR = env('ETH_SAFE_ADDR')

BNB_SAFE_ADDR = env('BNB_SAFE_ADDR')

TRX_SAFE_ADDR = env('TRX_SAFE_ADDR')


BTC_BLOCK_GENERATION_TIME = 5 * 60.0
BTC_NODE_CONNECTION_RETRIES = 5
SAT_PER_BYTES_UPDATE_PERIOD = 120  # 2min
SAT_PER_BYTES_MIN_LIMIT = 3
SAT_PER_BYTES_MAX_LIMIT = 60
SAT_PER_BYTES_RATIO = 1


# Ethereum & ERC
WEB3_INFURA_API_KEY = env('INFURA_API_KEY', default='')
WEB3_INFURA_API_SECRET = env('INFURA_API_SECRET', default='')
ETH_CHAIN_ID = 1  # 3 for Ropsten
ETH_TX_GAS = 21000
ETH_BLOCK_GENERATION_TIME = 15.0
ETH_ERC20_ACCUMULATION_PERIOD = 60.0
ETH_GAS_PRICE_UPDATE_PERIOD = 30
ETH_GAS_PRICE_COEFFICIENT = 0.1
ETH_MAX_GAS_PRICE = 200000000000  # wei
ETH_MIN_GAS_PRICE = 20000000000  # wei

BNB_CHAIN_ID = 56
BNB_TX_GAS = 21000
BNB_BEP20_ACCUMULATION_PERIOD = 60
BNB_BLOCK_GENERATION_TIME = 15
BNB_GAS_PRICE_UPDATE_PERIOD = 60
BNB_GAS_PRICE_COEFFICIENT = 0.1
BNB_MAX_GAS_PRICE = 300000000000
BNB_MIN_GAS_PRICE = 5000000000
BNB_RPC_ENDPOINTS = [
    'https://bsc-dataseed.binance.org/',
    'https://bsc-dataseed1.defibit.io/',
    'https://bsc-dataseed1.ninicoin.io/',
]
FIAT_RPC_ENDPOINTS = [
    'https://mercadopago.com/',
]

TRX_NET_FEE = 3_000_000  # 3 TRX
TRC20_FEE_LIMIT = 100_000_000  # 100 TRX
TRX_BLOCK_GENERATION_TIME = 3
TRX_TRC20_ACCUMULATION_PERIOD = 5 * 60.0

TRONGRID_API_KEY = [env('TRONGRID_API_KEY', default='')]
ETHERSCAN_KEY = env('ETHERSCAN_KEY', default='')
BSCSCAN_KEY = env('BSCSCAN_KEY', default='')

LATEST_ADDRESSES_REGENERATION = timezone.datetime(2021, 1, 28, 11, 20)

CRYPTO_KEY_OLD = env('CRYPTO_KEY_OLD', default='')
CRYPTO_KEY = env('CRYPTO_KEY', default='')

# Infura auto client setup
os.environ['WEB3_INFURA_API_KEY'] = WEB3_INFURA_API_KEY
os.environ['WEB3_INFURA_API_SECRET'] = WEB3_INFURA_API_SECRET
os.environ['WEB3_INFURA_SCHEME'] = 'https'

MIN_COST_ORDER_CANCEL = 0.0000001
