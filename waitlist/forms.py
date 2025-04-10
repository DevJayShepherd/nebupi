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


class WaitlistEntryForm(forms.Form):
    email = forms.EmailField(label=False,
                             required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Email',
                                        'class': 'py-3 px-4 block w-full border-gray-200 rounded-lg text-sm font-semibold bg-white focus:border-orange-500 focus:ring-orange-500 focus:ring-2 disabled:opacity-50 disabled:pointer-events-none dark:bg-white dark:text-gray-800 dark:border-orange-300 dark:focus:ring-orange-500 shadow-sm hover:shadow-md transition-all duration-200'}))
