from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler
from . import views
from .slack.listeners import app

handler = SlackRequestHandler(app=app)

@csrf_exempt
def slack_events_handler(request):
    return handler.handle(request)


def slack_oauth_handler(request):
    return handler.handle(request)

urlpatterns = [
    path("slack/events", slack_events_handler, name="slack_events"),
    path("slack/install", slack_oauth_handler, name="slack_install"),
    path("slack/oauth_redirect", slack_oauth_handler, name="slack_authorize"),

    path("strava/oauth_redirect", views.strava_oauth_redirect, name="strava_authorize")
]