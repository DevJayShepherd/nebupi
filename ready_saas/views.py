from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# orders
from orders.models import Plan


def landing(request):
    plan_tier_1 = Plan.objects.get(tier=1)
    plan_tier_2 = Plan.objects.get(tier=2)
    plan_tier_3 = Plan.objects.get(tier=3)

    return render(request, 'landing.html', {"plan_tier_1": plan_tier_1,
                                            "plan_tier_2": plan_tier_2,
                                            "plan_tier_3": plan_tier_3})


@login_required(login_url='email_login')
def dashboard(request):
    return render(request, 'dashboard.html')
