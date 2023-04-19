import logging

from django.conf import settings
from django.db import transaction

from eth_account import Account
from eth_utils.curried import combomethod
from eth_utils.curried import keccak
from eth_utils.curried import text_if_str
from eth_utils.curried import to_bytes
from pywallet import wallet as pwallet

from web3 import Web3
from solcx import compile_source, install_solc, compile_files
from solcx.exceptions import SolcNotInstalled
try:
    from .connection import get_w3_connection
except:
    from connection import get_w3_connection

from core.consts.currencies import BlockchainAccount
from lib.cipher import AESCoderDecoder

log = logging.getLogger(__name__)

class SmartContractWallet():
    def __init__(self) -> None:
        # Connect to the local Ethereum node
        # web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
        self.web3 = get_w3_connection()
        self.compile_contract('contract.sol')

    def compile_contract(self, contract_filename='wallet.sol'):
        """ Compiles the smart contract source code
        """
        import os
        from solcx import compile_standard

        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        install_solc('0.8.19')
        file = SCRIPT_DIR + '/' + contract_filename
        input = {
            'language': 'Solidity',
            'sources': {
                f'[{file}]': {
                'content': open(file).read()
                }
            },
            'settings': {
                'outputSelection': {
                '*': {
                    '*': ['*']
                }
                }
            }
        }
        compiled = compile_standard(input)
        # Get the contract ABI and bytecode
        contract_interface = compiled['<stdin>:CustomerBalance']
        self.abi = contract_interface['abi']
        self.bytecode = contract_interface['bin']
        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode)

    def create_wallet(self, user_id, currency):
        # Deploy the smart contract
        tx_hash = self.contract.constructor().transact()
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        code = 1
        return contract_address, code

    def deposit(self, customer_address='0x1234567890123456789012345678901234567890', ccy='USD', amount=0):
        # Interact with the smart contract
        currency = self.web3.toBytes(text=ccy)
        self.contract.functions.deposit(currency, amount).transact({'from': customer_address})
    
    def get_balance(self, contract_address, currency) :
        balance = self.contract.functions.getBalance(contract_address, currency).call()
        logging.debug(f"Customer {contract_address} has a balance of {balance} {currency.decode('utf-8')}")

def create_eth_address():
    while 1:
        account = PassphraseAccount.create(pwallet.generate_mnemonic())

        encrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).encrypt(
            Web3.toHex(account.privateKey)
        )
        decrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).decrypt(encrypted_key)

        if decrypted_key.startswith('0x') and len(decrypted_key) == 66:
            break
    return account.address, encrypted_key


def create_new_blockchain_account() -> BlockchainAccount:
    address, encrypted_pk = create_eth_address()
    return BlockchainAccount(
        address=address,
        private_key=AESCoderDecoder(settings.CRYPTO_KEY).decrypt(encrypted_pk),
    )


@transaction.atomic
def get_or_create_fiat_wallet(user_id, currency, is_new=False):
    """
    Make new user wallet and related objects if not exists
    """
    # implicit logic instead of get_or_create
    from core.models.cryptocoins import UserWallet

    user_wallet = UserWallet.objects.filter(
        user_id=user_id,
        currency=currency,
        # blockchain_currency='ETH',
        is_old=False,
    ).order_by('-id').first()

    if not is_new and user_wallet is not None:
        return user_wallet



    scw = SmartContractWallet()
    address, encrypted_key = scw.create_wallet()

    user_wallet = UserWallet.objects.create(
        user_id=user_id,
        address=address,
        private_key=encrypted_key,
        currency=currency,
        # blockchain_currency='ETH'
    )

    return user_wallet


@transaction.atomic
def get_or_create_erc20_wallet(user_id, currency, is_new=False):
    from core.models.cryptocoins import UserWallet

    erc20_wallet = UserWallet.objects.filter(
        user_id=user_id,
        currency=currency,
        blockchain_currency='ETH',
        is_old=False,
    ).order_by('-id').first()

    if not is_new and erc20_wallet is not None:
        return erc20_wallet

    address, encrypted_key = create_eth_address()

    erc20_wallet = UserWallet.objects.create(
        user_id=user_id,
        address=address,
        private_key=encrypted_key,
        currency=currency,
        blockchain_currency='ETH',
    )

    return erc20_wallet


class PassphraseAccount(Account):

    @combomethod
    def create(self, passphrase):
        extra_key_bytes = text_if_str(to_bytes, passphrase)
        key_bytes = keccak(extra_key_bytes)
        return self.privateKeyToAccount(key_bytes)


def get_wallet_data(user_id, currency, is_new=False):
    from core.models.cryptocoins import UserWallet

    wallet = get_or_create_eth_wallet(user_id, is_new=is_new)
    return UserWallet.objects.filter(id=wallet.id)


def eth_wallet_creation_wrapper(user_id, is_new=False, **kwargs):
    from core.models.cryptocoins import UserWallet

    wallet = get_or_create_eth_wallet(user_id, is_new=is_new)
    return UserWallet.objects.filter(id=wallet.id)


def erc20_wallet_creation_wrapper(user_id, currency, is_new=False, **kwargs):
    from core.models.cryptocoins import UserWallet

    wallet = get_or_create_erc20_wallet(user_id, currency=currency, is_new=is_new)
    return UserWallet.objects.filter(id=wallet.id)

def is_valid_eth_address(address):
    return Web3.isAddress(address)