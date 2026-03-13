"""
Reports: list (search/filter), detail (map + contact), create, edit, delete.
Permissions: only reporter can edit/delete own reports; admin can moderate.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from django.http import HttpResponseForbidden

from accounts.models import get_user_role, is_admin_user
from .models import PetReport, PetImage, ContactRequest
from .forms import PetReportForm, ContactRequestForm


def _can_edit_report(user, report):
    if not user or not user.is_authenticated:
        return False
    if is_admin_user(user):
        return True
    return report.reporter_user_id == user.id


def _save_report_images(request, report, start_order):
    """Save uploaded images for a report; show message if any fail (e.g. read-only disk). Returns count saved."""
    saved = 0
    for i, f in enumerate(request.FILES.getlist('images')[:10]):
        try:
            PetImage.objects.create(report=report, image=f, order=start_order + i)
            saved += 1
        except (OSError, IOError):
            messages.warning(
                request,
                f'Photo "{getattr(f, "name", "?")}" could not be saved (storage error). Try again or use another image.',
            )
    return saved


def report_list(request):
    """Reports list with filters: type, species, city/region, status, date."""
    qs = PetReport.objects.all().select_related('reporter_user').prefetch_related('images')
    # Filters from GET
    report_type = request.GET.get('type')
    if report_type in (PetReport.REPORT_LOST, PetReport.REPORT_FOUND):
        qs = qs.filter(report_type=report_type)
    species = request.GET.get('species')
    if species in dict(PetReport.SPECIES_CHOICES):
        qs = qs.filter(species=species)
    status = request.GET.get('status')
    if status in (PetReport.STATUS_OPEN, PetReport.STATUS_RESOLVED):
        qs = qs.filter(status=status)
    city = request.GET.get('city', '').strip()
    if city:
        qs = qs.filter(location_text__icontains=city)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(description__icontains=q) | Q(breed__icontains=q) | Q(location_text__icontains=q)
        )
    paginator = Paginator(qs, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'reports/report_list.html', {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'filters': {
            'type': report_type,
            'species': species,
            'status': status,
            'city': city,
            'q': q,
        },
    })


def report_detail(request, pk):
    """Report detail: photos, description, map marker, contact form."""
    report = get_object_or_404(PetReport, pk=pk)
    contact_form = ContactRequestForm()
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'contact_form': contact_form,
        'can_edit': _can_edit_report(request.user, report),
    })


@require_http_methods(['GET', 'POST'])
def contact_request_create(request, pk):
    """Submit contact form for a report (guest or registered)."""
    report = get_object_or_404(PetReport, pk=pk)
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            ContactRequest.objects.create(
                from_name=form.cleaned_data['from_name'],
                from_email=form.cleaned_data['from_email'],
                message_text=form.cleaned_data['message_text'],
                from_user=request.user if request.user.is_authenticated else None,
                to_report=report,
            )
            messages.success(request, 'Your message was sent. The reporter may contact you.')
            return redirect('reports:detail', pk=report.pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ContactRequestForm(initial={
            'from_name': request.user.get_full_name() or request.user.username if request.user.is_authenticated else '',
            'from_email': request.user.email if request.user.is_authenticated else '',
        })
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'contact_form': form,
        'can_edit': _can_edit_report(request.user, report),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def report_create(request):
    """Create lost/found report (registered user only)."""
    if request.method == 'POST':
        form = PetReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter_user = request.user
            report.status = PetReport.STATUS_OPEN
            report.save()
            # Save uploaded photos (multiple via name="images")
            n = _save_report_images(request, report, 0)
            messages.success(request, 'Report created.' + (f' {n} photo(s) added.' if n else ''))
            return redirect('reports:detail', pk=report.pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PetReportForm()
    return render(request, 'reports/report_form.html', {'form': form, 'report': None})


@login_required
@require_http_methods(['GET', 'POST'])
def report_edit(request, pk):
    """Edit report — only owner or admin."""
    report = get_object_or_404(PetReport, pk=pk)
    if not _can_edit_report(request.user, report):
        return HttpResponseForbidden('You cannot edit this report.')
    if request.method == 'POST':
        form = PetReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            start_order = report.images.count()
            n = _save_report_images(request, report, start_order)
            messages.success(request, 'Report updated.' + (f' {n} photo(s) added.' if n else ''))
            return redirect('reports:detail', pk=report.pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PetReportForm(instance=report)
    return render(request, 'reports/report_form.html', {'form': form, 'report': report})


@login_required
@require_POST
def report_delete(request, pk):
    """Delete report — only owner or admin."""
    report = get_object_or_404(PetReport, pk=pk)
    if not _can_edit_report(request.user, report):
        return HttpResponseForbidden('You cannot delete this report.')
    report.delete()
    messages.success(request, 'Report deleted.')
    return redirect('accounts:dashboard')
