from django.shortcuts import render
from reports.models import PetReport


def home(request):
    """Home page: latest lost/found + quick filters."""
    latest = PetReport.objects.filter(status=PetReport.STATUS_OPEN).order_by('-created_at')[:12]
    return render(request, 'core/home.html', {'latest_reports': latest})
