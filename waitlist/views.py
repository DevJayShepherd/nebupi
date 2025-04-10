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
