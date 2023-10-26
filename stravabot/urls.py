from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/slack/authorize", views.authorize_slack, name="authorize_slack")
]