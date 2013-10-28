from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def user(request):
    return redirect('fitmarkers.user.views.dashboard')


@login_required
def dashboard(request):
    return render(request, 'user_dashboard.html')
