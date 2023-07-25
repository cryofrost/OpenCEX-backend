import mercadopago
# from mercadopago.config import RequestOptions
from core.lib.inouts import BasePayGate
# import core.models.inouts.sci
from django.db.transaction import atomic
from django.contrib.auth.models import User
from django.conf import settings


MP_TOKEN = "TEST-161193485748495-030212-39f4663c69d1c5f7831bfcbeb85d0706-1044069535"
MP_KEY = "TEST-a2ae9c36-db08-4b9b-8463-777910878b28"

class MercadoPago(BasePayGate):
	ID = 1
	NAME = 'MercadoPago'
	SCI_URL = None
	ALLOW_CURRENCY = ['MXN']
	
	def update_topup(cls, request):
		sdk = mercadopago.SDK(MP_TOKEN)
		if 'get_preference' in request:
			# Create an item in the preference
			preference_data = {
			# the "purpose": "wallet_purchase", allows only logged in payments
			# to allow guest payments, you can omit this property
				"purpose": "wallet_purchase",
				"items": [
					{
						"title": "My test Item",
						"quantity": 1,
						"unit_price": 75.76,
						"id": request['get_preference']
					}
				]
			}

			preference_response = sdk.preference().create(preference_data)
			preference = preference_response["response"]
			return preference 

		payment_data = request
		
		if 'description' not in request:
			payment_data['description'] = f'payer: {request["payer"]}, amount: {request["transaction_amount"]}'
		payment_data["transaction_amount"] = float(payment_data["transaction_amount"])
		payment_response = sdk.payment().create(payment_data)
		payment = payment_response["response"]
  
		if 'status' in payment:
			with atomic():
				top_up = cls()
				top_utx_p = cls()
				top_up.amount = request['transaction_amount']
				top_up.tx_amount = payment['transaction_amount']
				# "PayGateTopup.tx" must be a "Transaction" instance.
				# top_up.tx = payment['transaction_details']
				top_up.tx_link = payment['transaction_details']['external_resource_url']
				top_up.created = payment['date_created']
				top_up.currency = payment['currency_id']
				
				top_up.data = payment['transaction_details']
		
				top_up.gate_id = MercadoPago.ID
				top_up.id = payment['id']
				# top_up.tx_id = payment['transaction_details']['verification_code']
				# top_up.tx_id = payment['id']
    
				user = User.objects.get(email__exact=payment_data['payer']['email'])
				top_up.user_id = user.id

				from core.models import Transaction
				from core.models.inouts.transaction import REASON_TOPUP
				from core.currency import Currency
    
				currency = Currency.get(payment['currency_id'])
				tx = Transaction.topup(user.id, currency, payment['transaction_amount'], {'1': 1}, reason=REASON_TOPUP)
				top_up.tx = tx
				top_up.tx_id = tx.id
    
				top_up.save()
			# top_up.gate = ID

		return payment
	
	def main(self):
		print(dir(self))

if __name__ == '__main__':
	m = MercadoPago()
	m.main()