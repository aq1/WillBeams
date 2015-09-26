from django.http import HttpResponse


def index(request):
    return HttpResponse('All set up <a href=/admin/>admin</a>')
