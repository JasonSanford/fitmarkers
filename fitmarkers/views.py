from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect


def home(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('fitmarkers.views.home')
