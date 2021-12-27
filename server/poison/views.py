from django.http import HttpRequest, HttpResponse

def index(request):
    # type: (HttpRequest) -> HttpResponse
    return HttpResponse("Web-app here")
