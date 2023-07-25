from solcx import compile_standard
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from eth_tester import PyEVMBackend
import json,os,pprint

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', '../../exchange.settings')


# try:
#     from .connection import get_w3_connection
# except:
#     from connection import get_w3_connection


# file = '/app/opencex/backend/sci/wallet/contract.sol'
file = '/app/sci/wallet/contract.sol'

input = {
  'language': 'Solidity',
  'sources': {
    f'{file}': {
      'content': open(file).read()
    }
  },
  'settings': {
    'outputSelection': {
      '*': {
        '*': ['*']
        # '*': ['abi', 'bin']
      }
    }
  }
}

def deploy_contract(w3, contract_interface):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['evm']['bytecode']['object']).constructor().transact()

    address = w3.eth.get_transaction_receipt(tx_hash)['contractAddress']
    return address


w3 = Web3(EthereumTesterProvider(PyEVMBackend()))
compiled = compile_standard(input)
contract_interface = compiled['contracts'][f'{file}']['CustomerBalance']
abi = contract_interface['abi']
bytecode = contract_interface['evm']['bytecode']['object']
address = deploy_contract(w3, contract_interface)
print(f'Deployed to: {address}\n')

store_var_contract = w3.eth.contract(address=address, abi=contract_interface["abi"])

gas_estimate = store_var_contract.functions.setVar(255).estimate_gas()
print(f'Gas estimate to transact with setVar: {gas_estimate}')

if gas_estimate < 100000:
     print("Sending transaction to setVar(255)\n")
     tx_hash = store_var_contract.functions.setVar(255).transact()
     receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
     print("Transaction receipt mined:")
     pprint.pprint(dict(receipt))
     print("\nWas transaction successful?")
     pprint.pprint(receipt["status"])
else:
     print("Gas cost exceeds 100000")