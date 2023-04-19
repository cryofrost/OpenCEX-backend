import mercadopago
from mercadopago.config import RequestOptions
from core.lib.inouts import BasePayGate

TOKEN = "TEST-161193485748495-030212-39f4663c69d1c5f7831bfcbeb85d0706-1044069535"

class MercadoPago(BasePayGate):
	ID = 1
	NAME = 'MercadoPago'
	SCI_URL = None
	ALLOW_CURRENCY = ['USDT', 'MXN']
	
	# def update_topup(self, cls, data):
	def update_topup(cls, data):
		# print(data)

		request_options = RequestOptions(access_token=TOKEN)
		sdk = mercadopago.SDK(TOKEN)
		card_data = {"cardholder": {
                    "name": "APRO"
                },
                    'Name': 'Visa', 'Number':	'4013540682746260',
                    'Security code': '123', 'Expiration date': '11/25',
                    'Name': 'APRO'}
		names = {'APRO': 'Approved payment',
                    'OTHE': 'Declined for general error',
                    'CONT': 'Pending payment',
                    'CALL': 'Declined with validation to authorize',
                    'FUND': 'Declined for insufficient amount',
                    'SECU': 'Declined for invalid security code',
                    'EXPI': 'Declined due to due date issue',
                    'FORM': 'Declined due to form error'}
		card = sdk.card_token().create(card_data, 	request_options=request_options)
		# print('Card: ', card)
  
		# payment_methods_response = sdk.payment_methods().list_all()
		# payment_methods = payment_methods_response["response"]
		# print(payment_methods)


		payment_data = {
		"transaction_amount": 100,
		"token": card['response']['id'],
		"description": "Payment testing",
		"payment_method_id": 'visa',
		"installments": 1,
		"payer": {
			"email": 'TEST_USER_1195263333@testuser.com',
			"entity_type": "individual",
			"type": "customer",
			"identification": {}
		}
	}
		result = sdk.payment().create(payment_data, request_options)
		payment = result["response"]
		payment['card'] = card

		# print(payment)
		return payment
	
	def main(self):
		print(dir(self))

if __name__ == '__main__':
	m = MercadoPago()
	m.main()

print('mercadopago init complete')
# import traceback
# for line in traceback.format_stack():
#         print(line.strip())