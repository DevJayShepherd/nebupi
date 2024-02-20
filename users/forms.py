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


from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from .models import User
from .tasks import send_email_task


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']

    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder':'Email'}))


class AsyncPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=False, max_length=254, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'autocomplete': 'email'}))

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        '''
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        '''
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        send_email_task.delay(subject=subject, message=body, recipient_list=[to_email])


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    new_password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
