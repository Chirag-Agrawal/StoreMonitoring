from django.http import HttpResponse

def test(request):
    print("hello from test")
    return HttpResponse("<h1>Hello , This is index page</h1>")