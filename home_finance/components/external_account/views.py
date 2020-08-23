from django.http import HttpResponse


def index(request):

    if request.method == 'POST':
        return HttpResponse("Hello, world. You're at the external account index with a POST.")
    return HttpResponse("Hello, world. You're at the external account index.")
