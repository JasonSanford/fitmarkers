from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect


def about(request):
    return render(request, 'about.html', {'tab': 'about'})


def home(request):
    if request.user.is_authenticated() and 'force_home' not in request.GET:
        return redirect('user_dashboard')
    return render(request, 'index.html', {'tab': 'home'})


def login(request):
    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('fitmarkers.views.home')
