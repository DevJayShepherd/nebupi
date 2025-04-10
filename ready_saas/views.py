from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# orders
from orders.models import Plan


def landing(request):
    # Import the waitlist form and model
    from waitlist.forms import WaitlistEntryForm
    from waitlist.models import WaitlistEntry
    from django.contrib import messages

    # Handle form submission
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
            else:
                # Email already exists, but still show a success message
                messages.success(request, "You're already on our waitlist!")
    else:
        # Create an empty form for GET requests
        form = WaitlistEntryForm()

    # Render the coming soon page with the form
    return render(request, 'coming_soon.html', {"form": form})


@login_required(login_url='email_login')
def dashboard(request):
    return render(request, 'dashboard.html')
