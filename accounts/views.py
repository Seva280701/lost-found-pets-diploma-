"""
Registration, login, logout, user dashboard.
Permissions: only own reports editable (enforced in reports app).
"""
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from reports.models import PetReport


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile created by signal with role=user
            login(request, user)
            messages.success(request, 'Account created. You can now create lost/found reports.')
            return redirect('core:home')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}.')
            next_url = request.GET.get('next') or reverse('core:home')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def dashboard(request):
    """User dashboard: My Reports (only own reports)."""
    reports = PetReport.objects.filter(reporter_user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard.html', {'reports': reports})
