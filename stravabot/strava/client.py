from os import access
from typing import Optional
from django.utils import timezone
from django.conf import settings
from stravalib.client import Client

from ..models import User

def get_strava_client(user_id: Optional[str]=None, refresh_buffer_minutes=120) -> Client:
    if user_id is None:
        return Client()

    user = User.objects.get(user_id=user_id)
    is_within_buffer = timezone.now() + timezone.timedelta(minutes=refresh_buffer_minutes) >= user.strava_token_expires_at
    if is_within_buffer and user.strava_refresh_token is not None:
        client = Client()
        refresh_response = client.refresh_access_token(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            refresh_token=user.strava_refresh_token,
        )
        user.strava_access_token = refresh_response['access_token']
        user.strava_refresh_token = refresh_response['refresh_token']
        user.strava_token_expires_at = refresh_response['expires_at']
        user.save()
    
    return Client(access_token=user.strava_access_token)
