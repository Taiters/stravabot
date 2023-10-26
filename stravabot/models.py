from uuid import uuid4
from django.db import models

class SlackAuthState(models.Model):
    state = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SlackInstallation(models.Model):
    pass
    

class SlackBot(models.Model):
    pass