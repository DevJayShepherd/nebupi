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


from django.db import models


class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0, help_text="Position in the waitlist")

    class Meta:
        ordering = ['position', 'timestamp']

    def __str__(self):
        return f"{self.email} - Position: {self.position}"
