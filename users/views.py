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
from django.contrib.auth import get_user_model, authenticate, login
from django.urls import reverse
from django.views.generic import FormView

from .forms import CustomUserCreationForm, EmailLoginForm
from .tasks import send_email_task

import sesame.utils


def SignUpView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add any post-save actions here

            # Authenticate and log in the user
            new_user = authenticate(username=user.email, password=form.cleaned_data['password1'])
            print("new_user:", new_user)
            if new_user is not None:
                login(request, new_user)

                # Redirect to 'next' parameter or a default view
                next_url = request.GET.get('next') or 'dashboard'
                print("next_url:", next_url)
                return redirect(next_url)
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


class EmailLoginView(FormView):
    template_name = "email_login.html"
    form_class = EmailLoginForm


    def get_user(self, email):
        """Find the user with this email address."""
        User = get_user_model()

        """ Note that we're using get_or_create here, so that if the user doesn't exist, we create them.
            Alternatively, you could only check if the user already exists (see code below),
            and if the user doesn't exist return None and handle that case in email_submitted (see commented code inside
            the email_submitted() method).

            try:
                return User.objects.get(email=email)
            except User.DoesNotExist:
                return None

        """

        return User.objects.get_or_create(email=email)[0]


    def create_link(self, user):
        """Create a login link for this user."""
        link = reverse("email_login_auth")
        link = self.request.build_absolute_uri(link)
        link += sesame.utils.get_query_string(user)
        return link


    def send_email(self, user, link):
        """Send an email with this login link to this user."""

        subject = "Log in to our app"
        body = f"""\
            Hello,

            Open the link below to log in:

                {link}

            Thank you!
            """
        to_email = user.email

        send_email_task.delay(subject=subject, message=body, recipient_list=[to_email])


    def email_submitted(self, email):
        user = self.get_user(email)
        # if user is None:
        #     # Ignore the case when no user is registered with this address.
        #     # Possible improvement: send an email telling them to register.
        #     print("user not found:", email)
        #     return
        link = self.create_link(user)
        self.send_email(user, link)


    def form_valid(self, form):
        self.email_submitted(form.cleaned_data["email"])
        return render(self.request, "email_login_success.html")
