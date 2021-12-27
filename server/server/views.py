from django.http import HttpRequest, HttpResponseRedirect

def index(request):
    # type: (HttpRequest) -> HttpResponseRedirect
    return HttpResponseRedirect('/poison')
