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


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# orders
from orders.models import Plan, Subscription, Product
from orders.paypal.paypal_helper import verify_paypal_webhook_event, process_paypal_webhook, create_order, capture_order
import orders.stripe.stripe_helper as stripe_helper

import os
import environ

# Setup environment variables with fallback to .env file
env = environ.Env()


def pricing(request):
    plan_tier_1 = Plan.objects.get(tier=1)
    plan_tier_2 = Plan.objects.get(tier=2)
    plan_tier_3 = Plan.objects.get(tier=3)

    return render(request, 'pricing.html', {"plan_tier_1": plan_tier_1,
                                            "plan_tier_2": plan_tier_2,
                                            "plan_tier_3": plan_tier_3})


@login_required(login_url='signup')
def checkout(request, plan_id):
    # Fetch the plan using the provided plan_id
    plan = get_object_or_404(Plan, id=plan_id)

    paypal_client_id = os.getenv('PAYPAL_CLIENT_ID', env('PAYPAL_CLIENT_ID'))

    context = {
        'plan': plan,
        'paypal_client_id': paypal_client_id
    }

    return render(request, 'checkout.html', context)


@login_required(login_url='signup')
def checkout_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    paypal_client_id = os.getenv('PAYPAL_CLIENT_ID', env('PAYPAL_CLIENT_ID'))

    context = {
        'product': product,
        'paypal_client_id': paypal_client_id
    }

    return render(request, 'checkout_product.html', context)


@login_required
def user_subscription(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        subscription = None

    # Pass the subscription to the template context
    context = {
        'subscription': subscription
    }

    return render(request, 'user_subscription.html', context)


'''
PayPal
'''

@csrf_exempt
def paypal_webhook_listener(request):
    if not verify_paypal_webhook_event(request):
        print("invalid PayPal webhook event received")
        return HttpResponse(status=400)
    else:
        print("valid PayPal webhook event received")

    return process_paypal_webhook(request)


def paypal_orders_create(request):
    print("creating paypal order")
    response = create_order(request)

    return JsonResponse(response)


def paypal_orders_capture(request, order_id):
    print("capturing paypal order")
    response = capture_order(request, order_id)

    return JsonResponse(response)


'''
Stripe
'''

@csrf_exempt
def stripe_webhook_listener(request):
    return stripe_helper.process_webhook(request)


def stripe_checkout_session_create(request):
    print("creating stripe checkout session")

    return stripe_helper.create_checkout_session(request)
