'''
Ready SaaS Source Code

Copyright 2023 Ready SaaS

Licensed under Ready SaaS Proprietary License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.readysaas.app/licenses/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


# django
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template

# orders
from orders.models import Plan, Subscription, SubscriptionStatus, Product

# users
from users.models import User
from users.tasks import send_email_task

import json
import os
import environ
import requests
import datetime

# Setup environment variables with fallback to .env file
env = environ.Env()


'''
SUBSCRIPTIONS
'''

SUBSCRIPTION_ACTIVATED = 'BILLING.SUBSCRIPTION.ACTIVATED'
SUBSCRIPTION_PAYMENT_FAILED = 'BILLING.SUBSCRIPTION.PAYMENT.FAILED'
SUBSCRIPTION_REACTIVATED = 'BILLING.SUBSCRIPTION.RE-ACTIVATED'
PAYMENT_SALE_COMPLETED = 'PAYMENT.SALE.COMPLETED'

SUBSCRIPTION_WEBHOOK_EVENTS_TO_HANDLE = [
    SUBSCRIPTION_ACTIVATED,
    SUBSCRIPTION_PAYMENT_FAILED,
    SUBSCRIPTION_REACTIVATED
]

PAYMENT_WEBHOOK_EVENTS_TO_HANDLE = [
    PAYMENT_SALE_COMPLETED
]


def get_subscription(subscription_id):
    # Set up your PayPal API credentials
    access_token = get_paypal_access_token()

    # PayPal API endpoint to fetch subscription details
    paypal_api_url = os.getenv('PAYPAL_API_URL', env('PAYPAL_API_URL'))
    url = paypal_api_url + f"/v1/billing/subscriptions/{subscription_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def process_paypal_webhook(request):

    def process_billing_event(event):
        subscription_details = event.get('resource', {})

        # Identify the corresponding user in the database
        try:
            user = User.objects.get(email=subscription_details['custom_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            # TODO handle case where User is not logged in
            return JsonResponse({'error': 'custom_id key not found'}, status=400)

        # Identify the corresponding plan in the database
        try:
            plan = Plan.objects.get(external_plan_id=subscription_details['plan_id'])
        except Plan.DoesNotExist:
            return JsonResponse({'error': 'Plan not found'}, status=404)

        # Update the subscription based on the event type
        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            # Payment is successful and the subscription is created.
            # Provision the subscription

            datetime_obj = datetime.datetime.strptime(subscription_details['create_time'], "%Y-%m-%dT%H:%M:%SZ")
            date_str = datetime_obj.strftime("%Y-%m-%d")

            subscription = Subscription.objects.create(
                subscription_id=subscription_details['id'],
                status=SubscriptionStatus.ACTIVE,
                plan=plan,
                user=user,
                start_date=date_str,
                end_date=subscription_details['billing_info']['next_billing_time'][:10],
            )
            print("subscription created")
            return JsonResponse({'message': 'Subscription created successfully'}, status=200)
        elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.FAILED':
            # The payment failed or the customer does not have a valid payment method.
            # The subscription becomes past_due. Notify your customer

            print("payment failed")
            subscription = Subscription.objects.get(user=user)
            subscription.status = SubscriptionStatus.PAST_DUE
            subscription.save()
            email_txt = get_template('emails/payment_failed_email.txt')
            message = email_txt.render({})
            send_email_task.delay(
                subject='Payment Failed',
                message=message,
                recipient_list=[subscription.user.email]
            )
        else:
            print("paypal event", event_type, "not handled")

        return JsonResponse({'message': 'Subscription updated successfully'}, status=200)


    def process_payment_event(event):
        subscription_details = event.get('resource', {})
        # Identify the corresponding user in the database
        try:
            user = User.objects.get(email=subscription_details['custom'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            # TODO handle case where User is not logged in
            return JsonResponse({'error': 'custom key not found'}, status=400)

        # Identify the corresponding subscription in the database
        try:
            subscription = Subscription.objects.get(user=user)
        except Subscription.DoesNotExist:
            return JsonResponse({'error': 'Subscription not found'}, status=404)

        # process the payment event
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.

        subscription.status = SubscriptionStatus.ACTIVE
        subscription.end_date = get_subscription(subscription.subscription_id)['billing_info']['next_billing_time'][:10]
        subscription.save()

        return JsonResponse({'message': 'Subscription updated successfully'}, status=200)


    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_type = event.get('event_type')

    print("processing paypal event", event_type)

    if event_type in SUBSCRIPTION_WEBHOOK_EVENTS_TO_HANDLE:
        return process_billing_event(event)
    elif event_type in PAYMENT_WEBHOOK_EVENTS_TO_HANDLE:
        return process_payment_event(event)

    return JsonResponse({'message': 'Subscription updated successfully'}, status=200)


def verify_paypal_webhook_event(request):
    """
    Verify the received PayPal webhook event.

    :param request: The webhook event request.
    :return: True if the event is verified, False otherwise.
    """

    body = request.body
    headers = request.headers

    # PayPal API endpoint for webhook verification
    paypal_api_url = os.getenv('PAYPAL_API_URL', env('PAYPAL_API_URL'))
    url = paypal_api_url + "/v1/notifications/verify-webhook-signature"

    # Prepare the verification payload
    verification_payload = {
        "transmission_id": headers["PAYPAL-TRANSMISSION-ID"],
        "transmission_time": headers["PAYPAL-TRANSMISSION-TIME"],
        "cert_url": headers["PAYPAL-CERT-URL"],
        "auth_algo": headers["PAYPAL-AUTH-ALGO"],
        "transmission_sig": headers["PAYPAL-TRANSMISSION-SIG"],
        "webhook_id": os.getenv('PAYPAL_WEBHOOK_ID', env('PAYPAL_WEBHOOK_ID')),
        "webhook_event": json.loads(body)
    }

    # Send the verification request to PayPal
    response = requests.post(url, json=verification_payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(get_paypal_access_token())
    })

    # Check the response
    if response.status_code == 200 and response.json().get("verification_status") == "SUCCESS":
        return True
    return False


'''
ONE TIME PAYMENT
'''

def create_order(request):
    payload = json.loads(request.body)
    product = get_object_or_404(Product, product_id=payload['product_id'])

    paypal_api_url = os.getenv('PAYPAL_API_URL', env('PAYPAL_API_URL'))
    url = paypal_api_url + "/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(get_paypal_access_token())
    }
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "{:.2f}".format(product.price)
                },
                "custom_id": request.user.email,
                "reference_id": product.product_id
            },
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    return response.json()


@login_required
def capture_order(request, order_id):
    paypal_api_url = os.getenv('PAYPAL_API_URL', env('PAYPAL_API_URL'))
    url = paypal_api_url + f"/v2/checkout/orders/{order_id}/capture"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(get_paypal_access_token()),
        # Uncomment one of these for negative testing in sandbox mode
        # "PayPal-Mock-Response": '{"mock_application_codes": "INSTRUMENT_DECLINED"}',
        # "PayPal-Mock-Response": '{"mock_application_codes": "TRANSACTION_REFUSED"}',
        # "PayPal-Mock-Response": '{"mock_application_codes": "INTERNAL_SERVER_ERROR"}',
    }

    response = requests.post(url, headers=headers)

    handle_payment_response(request.user, response)

    return response.json()


def handle_payment_response(user, response):
    '''
    Use this method to handle the payment response from PayPal.
    You can use the user session to identify the user and deliver their purchase, email them a thank you message, etc.
    '''
    if response.json().get("status") == "COMPLETED":
        product_id = response.json().get("purchase_units")[0].get("reference_id")
        product = Product.objects.get(product_id=product_id)

        print(f"{user.email} just purchased {product.display_name}")

    return


'''
AUTH
'''

def get_paypal_access_token():
    """
    Obtain an access token from PayPal.

    :return: Access token string or None if the request fails.
    """

    # PayPal API endpoint for obtaining an access token
    paypal_api_url = os.getenv('PAYPAL_API_URL', env('PAYPAL_API_URL'))
    url = paypal_api_url + "/v1/oauth2/token"

    # Basic Authentication using client_id and client_secret
    paypal_client_id = os.getenv('PAYPAL_CLIENT_ID', env('PAYPAL_CLIENT_ID'))
    paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET', env('PAYPAL_CLIENT_SECRET'))
    auth = (paypal_client_id, paypal_client_secret)

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, auth=auth, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    return None
