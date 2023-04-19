from solcx import compile_source, install_solc, compile_files, compile_standard
import json

file = '/app/opencex/backend/sci/wallet/wallet.sol'

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


# compiled = compile_files(file, output_dir='.', allow_empty=True)
compiled = compile_standard(input)
print(compiled)