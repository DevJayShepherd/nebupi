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


import environ

env = environ.Env(
    DEBUG=(bool, False),
    GA_TRACKING_ID=(str, ''),
)


def is_debug(request):
    return {'is_debug': env('DEBUG')}


def ga_tracking_id(request):
    return {'ga_tracking_id': env('GA_TRACKING_ID')}
