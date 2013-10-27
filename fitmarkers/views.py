from django.http import HttpResponse


def home(request):
    return HttpResponse('Yo dawg.<br><br><a href="/login/runkeeper">Log in</a>')
