from django.db import models

from stravabot.models import User

class SlackBot(models.Model):
    enterprise_id = models.CharField(null=True, max_length=32)
    enterprise_name = models.TextField(null=True)
    team_id = models.CharField(null=True, max_length=32)
    team_name = models.TextField(null=True)
    bot_token = models.TextField(null=True)
    bot_refresh_token = models.TextField(null=True)
    bot_token_expires_at = models.DateTimeField(null=True)
    bot_id = models.CharField(null=True, max_length=32)
    bot_user_id = models.CharField(null=True, max_length=32)
    bot_scopes = models.TextField(null=True)
    is_enterprise_install = models.BooleanField(null=True)
    installed_at = models.DateTimeField(null=False, auto_now_add=True)

    users = models.ManyToManyField(User)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enterprise_id", "team_id"], name="unique_enterprise_and_team")
        ]
