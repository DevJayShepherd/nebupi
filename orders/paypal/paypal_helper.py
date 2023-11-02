# django
from django.http import JsonResponse

# orders
from orders.models import Plan, Subscription, SubscriptionStatus, PlanFrequencyChoices
from orders.tasks import send_email_task

# users
from users.models import User

import json
import environ
import requests
import datetime

env = environ.Env()


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


def process_paypal_webhook(request):
    def resolve_end_date(plan):
        if plan.billing_frequency == PlanFrequencyChoices.MONTHLY:
            return datetime.date.today() + datetime.timedelta(days=30)
        elif plan.billing_frequency == PlanFrequencyChoices.YEARLY:
            return datetime.date.today() + datetime.timedelta(days=365)
        else:
            return None


    def process_billing_event(event):
        # Identify the corresponding user in the database
        subscription_details = event.get('resource', {})
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

        # Identify the corresponding subscription in the database
        try:
            subscription = Subscription.objects.get(user=user)
        except Subscription.DoesNotExist:
            if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
                datetime_obj = datetime.datetime.strptime(subscription_details['create_time'], "%Y-%m-%dT%H:%M:%SZ")
                date_str = datetime_obj.strftime("%Y-%m-%d")

                subscription = Subscription.objects.create(
                    subscription_id=subscription_details['id'],
                    status=SubscriptionStatus.ACTIVE,
                    plan=plan,
                    user=user,
                    start_date=date_str,
                    end_date=resolve_end_date(plan)
                )
                print("subscription created")
                return JsonResponse({'message': 'Subscription created successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Subscription not found'}, status=404)

        # Update the subscription based on the event type
        if event_type == 'BILLING.SUBSCRIPTION.RE-ACTIVATED':
            subscription.status = SubscriptionStatus.ACTIVE
            message = 'Your subscription has been reactivated. Thank you.'
            send_email_task.delay(
                subject='Subscription Reactivated',
                message=message,
                recipient_list=[subscription.user.email]
            )
        elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.FAILED':
            print("payment failed")
            message = f'Your payment for {subscription.plan.name} has failed. ' \
                      f'Please update your payment details to continue using our service. Thank you.'
            send_email_task.delay(
                subject='Payment Failed',
                message=message,
                recipient_list=[subscription.user.email]
            )
        else:
            print("paypal event", event_type, "not handled")

        subscription.save()

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

        subscription.status = SubscriptionStatus.ACTIVE
        subscription.end_date = resolve_end_date(subscription.plan)
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
    url = env('PAYPAL_API_URL') + "/v1/notifications/verify-webhook-signature"

    # Prepare the verification payload
    verification_payload = {
        "transmission_id": headers["PAYPAL-TRANSMISSION-ID"],
        "transmission_time": headers["PAYPAL-TRANSMISSION-TIME"],
        "cert_url": headers["PAYPAL-CERT-URL"],
        "auth_algo": headers["PAYPAL-AUTH-ALGO"],
        "transmission_sig": headers["PAYPAL-TRANSMISSION-SIG"],
        "webhook_id": env('PAYPAL_WEBHOOK_ID'),
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


def get_paypal_access_token():
    """
    Obtain an access token from PayPal.

    :return: Access token string or None if the request fails.
    """

    # PayPal API endpoint for obtaining an access token
    url = env('PAYPAL_API_URL') + "/v1/oauth2/token"

    # Basic Authentication using client_id and client_secret
    auth = (env('PAYPAL_CLIENT_ID'), env('PAYPAL_CLIENT_SECRET'))

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
