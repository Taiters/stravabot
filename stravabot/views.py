from django.http import HttpResponse

def strava_oauth_redirect(request):
    return HttpResponse("Hello!")