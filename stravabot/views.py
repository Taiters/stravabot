from django.shortcuts import render

def index(request):
    return render(request, 'stravabot/index.html', {
        'slack_auth_url': '1234',
    })