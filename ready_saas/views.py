from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# orders
from orders.models import Plan

# waitlist
from waitlist.models import WaitlistEntry
from waitlist.forms import WaitlistEntryForm


def landing(request):
    # Handle form submission for the waitlist
    if request.method == 'POST':
        form = WaitlistEntryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if the email is already in the waitlist
            if not WaitlistEntry.objects.filter(email=email).exists():
                # Add email to the waitlist
                position = WaitlistEntry.objects.count() + 1
                WaitlistEntry.objects.create(email=email, position=position)
                messages.success(request, "Done! You're on the waitlist.")
            # Don't redirect, just render the template with the success message
            return render(request, 'coming_soon.html', {'form': form})

    # Temporarily render the coming_soon.html template as the main page
    # until the rest of the app is ready
    form = WaitlistEntryForm()
    return render(request, 'coming_soon.html', {'form': form})

    # Original landing page code (commented out)
    # plan_tier_1 = Plan.objects.get(tier=1)
    # plan_tier_2 = Plan.objects.get(tier=2)
    # plan_tier_3 = Plan.objects.get(tier=3)
    # return render(request, 'landing.html', {"plan_tier_1": plan_tier_1,
    #                                         "plan_tier_2": plan_tier_2,
    #                                         "plan_tier_3": plan_tier_3})


@login_required(login_url='email_login')
def dashboard(request):
    return render(request, 'dashboard.html')
