from django.db import models
from django.contrib import admin
from django_cryptography.fields import encrypt

class User(models.Model):
    strava_athlete_id = models.CharField(max_length=128, unique=True)
    strava_access_token = encrypt(models.CharField(max_length=128))
    strava_refresh_token = encrypt(models.CharField(max_length=128))
    strava_token_expires_at = models.DateTimeField()

admin.site.register(User)

from stravabot.slack.models import *