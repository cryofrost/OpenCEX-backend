import os
import logging

from django.conf import settings
from django.db import models,transaction

# from eth_account import Account
# from eth_utils.curried import combomethod
# from eth_utils.curried import keccak
# from eth_utils.curried import text_if_str
# from eth_utils.curried import to_bytes
# from pywallet import wallet as pwallet


# from web3 import Web3
# from solcx import install_solc, compile_standard
# from solcx.exceptions import SolcNotInstalled
# try:
#     from .connection import get_w3_connection
# except:
#     from connection import get_w3_connection

# from core.consts.currencies import BlockchainAccount
# from lib.cipher import AESCoderDecoder

log = logging.getLogger(__name__)

# class SmartContractWallet():
#     def __init__(self) -> None:
#         # Connect to the local Ethereum node
#         self.web3 = get_w3_connection()
#         self.compile_contract('contract.sol')

#     def compile_contract(self, contract_filename='wallet.sol'):
#         """ Compiles the smart contract source code
#         """
#         SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#         install_solc('0.8.19')
#         file = SCRIPT_DIR + '/' + contract_filename
#         input = {
#             'language': 'Solidity',
#             'sources': {
#                 f'{file}': {
#                 'content': open(file).read()
#                 }
#             },
#             'settings': {
#                 'outputSelection': {
#                 '*': {
#                     '*': ['*']
#                 }
#                 }
#             }
#         }
#         compiled = compile_standard(input)
#         contract_interface = compiled['contracts'][f'{file}']['CustomerBalance']
#         self.abi = contract_interface['abi']
#         self.bytecode = contract_interface['evm']['bytecode']['object']

#     def create_wallet(self, user_id, currency):
#         # Deploy the smart contract
#         # ns.setup_address('jasoncarver.eth', '0x5B2063246F2191f18F2675ceDB8b28102e957458')
       
#         # self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode)
#         # new_addr = create_eth_address()
#         #tx_hash = self.contract([new_addr], 0).constructor().transact()
#         #tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
#         #contract_address = tx_receipt.contractAddress
#         code = 1
#         tx_hash = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor().transact()
#         contract_address = self.web3.eth.get_transaction_receipt(tx_hash)['contractAddress']
#         return contract_address, code

#     def deposit(self, customer_address='0x1234567890123456789012345678901234567890', ccy='USD', amount=0):
#         # Interact with the smart contract
#         currency = self.web3.toBytes(text=ccy)
#         self.contract.functions.deposit(currency, amount).transact({'from': customer_address})
    
#     def get_balance(self, contract_address, currency) :
#         balance = self.contract.functions.getBalance(contract_address, currency).call()
#         logging.debug(f"Customer {contract_address} has a balance of {balance} {currency.decode('utf-8')}")

# class Balance(models.Model):
#     currency = models.CharField(max_length=10)
#     amount = models.DecimalField(max_digits=30, decimal_places=10)
#     amount_in_orders = models.DecimalField(max_digits=30, decimal_places=10, default=0)

#     class Meta:
#         unique_together = ('id', 'currency')

#     @classmethod
#     def update_balance(cls, id, currency, amount):
#         with transaction.atomic():
#             balance, created = cls.objects.select_for_update().get_or_create(id=id, currency=currency)
#             balance.amount += amount
#             balance.save()

#         return balance.amount

#     @classmethod
#     def get_balance(cls, id, currency):
#         try:
#             balance = cls.objects.get(id=id, currency=currency)
#             return balance.amount
#         except cls.DoesNotExist:
#             return None

# class UserBalance(models.Model):
#     user_id = models.IntegerField()
#     currency = models.CharField(max_length=3)
#     balance = models.DecimalField(max_digits=18, decimal_places=8)

#     class Meta:
#         unique_together = ('user_id', 'currency')

#     @classmethod
#     def update_balance(cls, user_id, currency, amount):
#         with transaction.atomic():
#             balance, created = cls.objects.select_for_update().get_or_create(user_id=user_id, currency=currency)
#             balance.balance += amount
#             balance.save()

#         return balance.balance

#     @classmethod
#     def get_balance(cls, user_id, currency):
#         try:
#             balance = cls.objects.get(user_id=user_id, currency=currency)
#             return balance.balance
#         except cls.DoesNotExist:
#             return None

# def create_eth_address():
#     while 1:
#         account = PassphraseAccount.create(pwallet.generate_mnemonic())

#         encrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).encrypt(
#             Web3.toHex(account.privateKey)
#         )
#         decrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).decrypt(encrypted_key)

#         if decrypted_key.startswith('0x') and len(decrypted_key) == 66:
#             break
#     return account.address, encrypted_key


# def create_new_blockchain_account() -> BlockchainAccount:
#     address, encrypted_pk = create_eth_address()
#     return BlockchainAccount(
#         address=address,
#         private_key=AESCoderDecoder(settings.CRYPTO_KEY).decrypt(encrypted_pk),
#     )


@transaction.atomic
def get_or_create_fiat_wallet(user_id, currency, is_new=False):
    """
    Make new user wallet and related objects if not exists
    """
    # implicit logic instead of get_or_create
    from core.models.fiat import UserFiatWallet


    user_wallet = UserFiatWallet.objects.filter(
        user_id=user_id,
        currency=currency,
        # blockchain_currency='ETH',
        is_old=False,
    ).order_by('-id').first()

    if not is_new and user_wallet is not None:
        return user_wallet

    # scw = SmartContractWallet()
    # address, encrypted_key = scw.create_wallet(user_id, currency)

    user_wallet = UserFiatWallet.objects.create(
        user_id=user_id,
        # address=address,
        # private_key=encrypted_key,
        currency=currency,
        amount=0,
        amount_in_orders=0,
        # blockchain_currency='ETH'
    )
    log.debug(f'User wallet created: {user_wallet}')

    return user_wallet


# @transaction.atomic
# def get_or_create_erc20_wallet(user_id, currency, is_new=False):
#     from core.models.cryptocoins import UserWallet

#     erc20_wallet = UserWallet.objects.filter(
#         user_id=user_id,
#         currency=currency,
#         blockchain_currency='ETH',
#         is_old=False,
#     ).order_by('-id').first()

#     if not is_new and erc20_wallet is not None:
#         return erc20_wallet

#     address, encrypted_key = create_eth_address()

#     erc20_wallet = UserWallet.objects.create(
#         user_id=user_id,
#         address=address,
#         private_key=encrypted_key,
#         currency=currency,
#         blockchain_currency='ETH',
#     )

#     return erc20_wallet


# class PassphraseAccount(Account):

#     @combomethod
#     def create(self, passphrase):
#         extra_key_bytes = text_if_str(to_bytes, passphrase)
#         key_bytes = keccak(extra_key_bytes)
#         return self.privateKeyToAccount(key_bytes)


# def get_wallet_data(user_id, currency, is_new=False):
#     from core.models.cryptocoins import UserWallet

#     wallet = get_or_create_eth_wallet(user_id, is_new=is_new)
#     return UserWallet.objects.filter(id=wallet.id)


def fiat_wallet_creation_wrapper(user_id, currency, is_new=False, **kwargs):
    from core.models.fiat import UserFiatWallet

    wallet = get_or_create_fiat_wallet(user_id, currency, is_new=is_new)
    return UserFiatWallet.objects.filter(id=wallet.id)


# def erc20_wallet_creation_wrapper(user_id, currency, is_new=False, **kwargs):
#     from core.models.cryptocoins import UserWallet

#     wallet = get_or_create_erc20_wallet(user_id, currency=currency, is_new=is_new)
#     return UserWallet.objects.filter(id=wallet.id)

# def is_valid_eth_address(address):
#     return Web3.isAddress(address)