from django.shortcuts import render


def home(request):
    return render(request, 'web/home.html')


def contato(request):
    return render(request, 'web/contato.html')


def login(request):
    return render(request, 'web/login.html')
