from django.shortcuts import render

# Create your views here.
def index(request):
    message = "Hello world!"

    return render(request, message)