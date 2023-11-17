from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# orders
from orders.models import Plan, Subscription
from orders.paypal.paypal_helper import verify_paypal_webhook_event, process_paypal_webhook

import environ

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

    paypal_client_id = env('PAYPAL_CLIENT_ID')

    context = {
        'plan': plan,
        'paypal_client_id': paypal_client_id,
        'external_plan_id': plan
    }

    return render(request, 'checkout.html', context)


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


@csrf_exempt
def paypal_webhook_listener(request):
    if not verify_paypal_webhook_event(request):
        print("invalid PayPal webhook event received")
        return HttpResponse(status=400)
    else:
        print("valid PayPal webhook event received")

    return process_paypal_webhook(request)
