from django.db import models

class User(models.Model):
    strava_athlete_id = models.CharField(max_length=128, unique=True)
    strava_access_token = models.CharField(max_length=128)
    strava_refresh_token = models.CharField(max_length=128)
    strava_token_expires_at = models.DateTimeField()

from stravabot.slack.models import *