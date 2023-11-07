from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import datetime
import base64
import requests

app = Flask(__name__)
api = Api(app)

# Safaricom Daraja API credentials

LNM_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
ACCESS_TOKEN = "5XFsu11FvmiT796yqrtarG2oEwnT"

class LipaNaMpesaAPI(Resource):
    def get(self):
        return "Welcome to Flask Lipa na M-pesa API"

api.add_resource(LipaNaMpesaAPI, "/")

# Creating Lipa na Mpesa routes
class LipaNaMpesa(Resource):
    def post(self):
        request_data = request.get_json()

        # Extracting data from the request payload

        business_shortcode = "174379"  # Update with your actual business shortcode
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        transaction_type = "CustomerPayBillOnline"
        amount = "1"
        # phone number
        party_a = "254797228429"  
        party_b = business_shortcode
        # Update with your actual phone number
        phone_number = "254797228429"  
        callback_url = "https://9da7-197-139-44-10.ngrok-free.app/lipa_na_mpesa_callback"
        account_reference = "CompanyXLTD"
        transaction_desc = "Payment of X"

        # Calculate password
        password = base64.b64encode((business_shortcode + LNM_PASSKEY + timestamp).encode()).decode()

        # Set header for M-pesa STK push request
        headers = {
            "Host": "sandbox.safaricom.co.ke",
            "Authorization": "Bearer " + ACCESS_TOKEN,
            "Content-Type": "application/json",
        }

        # Set up STK push payload
        stk_push_payload = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": amount,
            "PartyA": party_a,
            "PartyB": party_b,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        # URL endpoint for STK push
        stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_push_url, json=stk_push_payload, headers=headers)

        print(response.text)

        # Handle response accordingly
        response_data = {
            "MerchantRequestID": response.json().get("MerchantRequestID"),
            "CheckoutRequestID": response.json().get("CheckoutRequestID"),
            "ResponseCode": response.json().get("ResponseCode"),
            "ResponseDescription": response.json().get("ResponseDescription"),
            "CustomerMessage": response.json().get("CustomerMessage"),
        }

        return jsonify(response_data)

api.add_resource(LipaNaMpesa, "/lipanampesa")


#route to handle callback url
class LipaNaMpesaCallBack(Resource):
    def post(self):
        callback_data = request.get_json()

        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]
        result_desc = callback_data['Body']['stkCallback']['ResultDesc']

        if result_code == 0:
            mpesa_receipt_number = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']

            #handle successful transcation
            return jsonify({'message': 'Transaction successful', 'mpesa_receipt_number': mpesa_receipt_number})
        else:
            # Handle failed transaction
            return jsonify({'message': 'Transaction failed', 'error_description': result_desc})

api.add_resource(LipaNaMpesaCallBack, "/lipanampesa_callback")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
