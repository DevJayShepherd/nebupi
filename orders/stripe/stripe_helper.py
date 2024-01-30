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
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

# orders
from orders.models import Plan, Subscription, SubscriptionStatus

# users
from users.models import User
from users.tasks import send_email_task
from users.utils.sesame_utils import create_login_link

import json
import stripe
import environ
import datetime

env = environ.Env(
    # set casting, default value
    STRIPE_SECRET_KEY=(str, 'DEFAULT')
)

stripe.api_key = env('STRIPE_SECRET_KEY')


def create_checkout_session(request):
    price_id = request.POST.get('priceId')

    session = stripe.checkout.Session.create(
        success_url=request.build_absolute_uri(reverse('thank_you')),
        cancel_url=request.build_absolute_uri(reverse('pricing')),
        customer_email=request.user.email if request.user.is_authenticated else None,
        mode='subscription',
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
    )

    return redirect(session.url, code=303)


def process_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    print('Received Stripe webhook! {}'.format(event.type))

    # Handle the event
    if event.type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.
        # Provision the subscription
        print("process checkout.session.completed")

        # get the customer email
        email = event.data.object.customer_details.email
        # find or create the user with this email
        user, created = User.objects.get_or_create(email=email)
        # get the subscription id
        subscription_id = event.data.object.subscription

        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']

        # Identify the corresponding plan in the database
        try:
            plan = Plan.objects.get(external_plan_id=price_id)
        except Plan.DoesNotExist:
            return JsonResponse({'error': 'Plan not found'}, status=404)


        # create subscription
        Subscription.objects.create(
            subscription_id=subscription_id,
            status=SubscriptionStatus.ACTIVE,
            plan=plan,
            user=user,
            start_date=datetime.datetime.fromtimestamp(subscription['current_period_start']),
            end_date=datetime.datetime.fromtimestamp(subscription['current_period_end']),
        )

        # build login link for user
        link = create_login_link(request, user)
        # send email to customer saying thank you and providing a link to login to the app
        send_email_task.delay(
            subject='Thank you!',
            message='Thank you for subscribing! Click the link to access your account. {}'.format(link),
            recipient_list=[user.email]
        )
    elif event.type == 'invoice.paid':
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.

        print("process invoice.paid")

        # get the customer email
        email = event.data.object.customer_details.email
        # find the user with this email or 404
        user = get_object_or_404(User, email=email)

        # update subscription status to active
        subscription = Subscription.objects.get(user=user)
        subscription.status = SubscriptionStatus.ACTIVE

        # update subscription next billing date
        next_billing_timestamp = event['data']['object']['lines']['data'][0]['period']['end']
        subscription.end_date = datetime.datetime.fromtimestamp(next_billing_timestamp)
        subscription.save()
    elif event.type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer
        print("process invoice.payment_failed")

        email = event.data.object.customer_details.email
        # find the user with this email or 404
        user = get_object_or_404(User, email=email)

        # update subscription status to past due
        subscription = Subscription.objects.get(user=user)
        subscription.status = SubscriptionStatus.PAST_DUE
        subscription.save()

        # send email to customer to update payment method
        send_email_task.delay(
            subject='Payment failed',
            message='Your payment method has failed. Please update your payment method.',
            recipient_list=[user.email]
        )
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
