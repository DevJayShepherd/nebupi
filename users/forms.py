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

    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'style':'margin-top: 10px;'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'style':'margin-top: 10px;'}))
    password = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'style':'margin-top: 10px;'}))


class AsyncPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=False, max_length=254, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class': 'form-control', 'autocomplete': 'email'}))

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
    new_password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
