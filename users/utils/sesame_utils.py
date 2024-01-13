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


# django
from django.urls import reverse

# sesame
import sesame.utils


def create_login_link(request, user):
    """Create a login link for this user."""
    link = reverse("email_login_auth")
    link = request.build_absolute_uri(link)
    link += sesame.utils.get_query_string(user)
    return link
