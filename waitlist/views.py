from django.shortcuts import render, redirect
from django.contrib import messages
from .models import WaitlistEntry
from .forms import WaitlistEntryForm


def join_waitlist(request):
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
                return redirect('join_waitlist')
    else:
        form = WaitlistEntryForm()

    return render(request, 'waitlist/join_waitlist.html', {'form': form})
