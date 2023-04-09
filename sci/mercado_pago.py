import mercadopago
from mercadopago.config import RequestOptions
from core.lib.inouts import BasePayGate

class MercadoPago(BasePayGate):
	ID = 1
	NAME = 'MercadoPago'
	SCI_URL = None
	ALLOW_CURRENCY = ['USDT', 'MXN']
	
	def update_topup(self, cls, data):
		print(cls, data)

	def main(self):
		TOKEN = "TEST-161193485748495-030212-39f4663c69d1c5f7831bfcbeb85d0706-1044069535"
		request_options = RequestOptions(access_token=TOKEN)
		sdk = mercadopago.SDK(TOKEN)
		card = sdk.card_token().create({'Name': 'Test'}, 	request_options=request_options)

		payment_data = {
		"transaction_amount": 100,
		"token": card['response']['id'],
		"description": "Payment description",
		"payment_method_id": 'visa',
		"installments": 1,
		"payer": {
			"email": 'test_user_123456@testuser.com'
		}
	}
		result = sdk.payment().create(payment_data, request_options)
		payment = result["response"]

		print(payment)
	
if __name__ == '__main__':
	m = MercadoPago()
	m.main()

print('mercadopago init complete')
# import traceback
# for line in traceback.format_stack():
#         print(line.strip())