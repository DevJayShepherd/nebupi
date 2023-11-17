from django import forms


class WaitlistEntryForm(forms.Form):
    email = forms.EmailField(label=False,
                             required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Email',
                                        'class': 'form-control'}))
