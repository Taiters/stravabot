from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.functional import lazy
from slack_sdk.web import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation

from stravabot.slack.stores import StravabotSlackOAuthStateStore

_get_redirect_uri = lazy(lambda: settings.BASE_URL + reverse('authorize_slack'), str)
state_store = StravabotSlackOAuthStateStore(expiration_seconds=300)
installation_store = FileInstallationStore(base_dir="./data")
authorize_url_generator = AuthorizeUrlGenerator(
    redirect_uri=_get_redirect_uri(),
    client_id=settings.SLACK_CLIENT_ID,
    scopes=[
        'channels:join',
        'channels:manage',
        'channels:read',
        'chat:write',
        'commands',
        'groups:read',
        'groups:write',
    ],
)


def index(request):
    state = state_store.issue()
    slack_auth_url = authorize_url_generator.generate(state)
    return render(request, 'stravabot/index.html', {
        'slack_auth_url': slack_auth_url,
    })


def authorize_slack(request):
    if "code" not in request.GET:
        return HttpResponse("Code missing", status=400)
    
    if state_store.consume(request.GET["state"]):
        client = WebClient()
        oauth_response = client.oauth_v2_access(
            client_id=settings.SLACK_CLIENT_ID,
            client_secret=settings.SLACK_CLIENT_SECRET,
            redirect_uri=_get_redirect_uri(),
            code=request.GET['code']
        )
        installed_enterprise = oauth_response.get("enterprise") or {}
        is_enterprise_install = oauth_response.get("is_enterprise_install")
        installed_team = oauth_response.get("team") or {}
        installer = oauth_response.get("authed_user") or {}
        incoming_webhook = oauth_response.get("incoming_webhook") or {}
        bot_token = oauth_response.get("access_token")
        bot_id = None
        enterprise_url = None
        if bot_token is not None:
            auth_test = client.auth_test(token=bot_token)
            bot_id = auth_test["bot_id"]
            if is_enterprise_install is True:
                enterprise_url = auth_test.get("url")

        installation = Installation(
            app_id=oauth_response.get("app_id"),
            enterprise_id=installed_enterprise.get("id"),
            enterprise_name=installed_enterprise.get("name"),
            enterprise_url=enterprise_url,
            team_id=installed_team.get("id"),
            team_name=installed_team.get("name"),
            bot_token=bot_token,
            bot_id=bot_id,
            bot_user_id=oauth_response.get("bot_user_id"),
            bot_scopes=oauth_response.get("scope"),
            user_id=installer.get("id"),
            user_token=installer.get("access_token"),
            user_scopes=installer.get("scope"),
            incoming_webhook_url=incoming_webhook.get("url"),
            incoming_webhook_channel=incoming_webhook.get("channel"),
            incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
            incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
            is_enterprise_install=is_enterprise_install,
            token_type=oauth_response.get("token_type"),
        )

        installation_store.save(installation)

        return HttpResponse("Thanks for installing this app!")
    else:
        return HttpResponse(f"State expired", status=400)