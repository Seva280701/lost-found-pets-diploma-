"""
Shelters: directory (list + map), shelter detail, dashboard (profile, pets CRUD, CSV import).
Permissions: only shelter owner can edit shelter and pets; only shelter role can access dashboard.
"""
import csv
import hashlib
import io
import json
import urllib.request
import urllib.parse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import HttpResponseForbidden, JsonResponse
from django.db import transaction

from accounts.models import get_user_role
from reports.forms import ContactRequestForm
from reports.models import ContactRequest
from .models import Shelter, ShelterPet
from .forms import ShelterForm, ShelterPetForm


def _get_shelter_for_user(user):
    """Return the shelter owned by this user (shelter role), or None."""
    if not user or not user.is_authenticated:
        return None
    if get_user_role(user) != 'shelter':
        return None
    return getattr(user, 'owned_shelter', None)


def _shelter_has_coords(s):
    """True if shelter has valid lat/lng for map (not None, not 0)."""
    if s.lat is None or s.lng is None:
        return False
    try:
        return float(s.lat) != 0 and float(s.lng) != 0
    except (TypeError, ValueError):
        return False


def directory(request):
    """Shelter directory: list + map with markers. Optionally geocode shelters missing coords."""
    shelters = list(Shelter.objects.all().order_by('name'))
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '') or ''
    # Backfill: geocode up to 5 shelters that have address but no valid coords (so they appear on map)
    if api_key:
        geocoded = 0
        for s in shelters:
            if geocoded >= 5:
                break
            if _shelter_has_coords(s):
                continue
            addr = ((s.address or '') + ', ' + (s.city or '')).strip(', ')
            if not addr:
                continue
            lat, lng = _geocode_address(addr)
            if lat is not None and lng is not None:
                Shelter.objects.filter(pk=s.pk).update(lat=lat, lng=lng)
                s.lat = lat
                s.lng = lng
                geocoded += 1
    shelters_json = json.dumps([
        {'id': s.id, 'name': s.name, 'lat': str(s.lat) if _shelter_has_coords(s) else None, 'lng': str(s.lng) if _shelter_has_coords(s) else None}
        for s in shelters
    ])
    return render(request, 'shelters/directory.html', {'shelters': shelters, 'shelters_json': shelters_json})


def shelter_detail(request, pk):
    """Shelter detail: info + pets + map + contact form."""
    shelter = get_object_or_404(Shelter, pk=pk)
    pets = shelter.pets.filter(status=ShelterPet.STATUS_IN_CARE)[:20]
    contact_form = ContactRequestForm()
    return render(request, 'shelters/shelter_detail.html', {
        'shelter': shelter, 'pets': pets, 'contact_form': contact_form,
    })


def pet_detail(request, pk):
    """Public shelter pet detail page."""
    pet = get_object_or_404(ShelterPet, pk=pk)
    return render(request, 'shelters/pet_detail.html', {'pet': pet})


@require_http_methods(['GET', 'POST'])
def shelter_contact(request, pk):
    """Submit contact form to a shelter (guest or registered)."""
    shelter = get_object_or_404(Shelter, pk=pk)
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            ContactRequest.objects.create(
                from_name=form.cleaned_data['from_name'],
                from_email=form.cleaned_data['from_email'],
                message_text=form.cleaned_data['message_text'],
                from_user=request.user if request.user.is_authenticated else None,
                to_shelter=shelter,
            )
            messages.success(request, 'Your message was sent. The shelter may contact you.')
            return redirect('shelters:detail', pk=shelter.pk)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ContactRequestForm(initial={
            'from_name': request.user.get_full_name() or request.user.username if request.user.is_authenticated else '',
            'from_email': request.user.email if request.user.is_authenticated else '',
        })
    pets = shelter.pets.filter(status=ShelterPet.STATUS_IN_CARE)[:20]
    return render(request, 'shelters/shelter_detail.html', {
        'shelter': shelter, 'pets': pets, 'contact_form': form,
    })


@login_required
def dashboard(request):
    """Shelter dashboard: only for users with shelter role and owned_shelter."""
    shelter = _get_shelter_for_user(request.user)
    if not shelter:
        messages.warning(request, 'You do not have a shelter account or your shelter is not set up.')
        return redirect('core:home')
    return render(request, 'shelters/dashboard.html', {'shelter': shelter})


@login_required
@require_http_methods(['GET', 'POST'])
def shelter_edit(request):
    """Edit shelter profile (owner only)."""
    shelter = _get_shelter_for_user(request.user)
    if not shelter:
        return HttpResponseForbidden('You do not have a shelter.')
    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shelter profile updated.')
            return redirect('shelters:dashboard')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ShelterForm(instance=shelter)
    return render(request, 'shelters/shelter_form.html', {'form': form, 'shelter': shelter})


@login_required
@require_http_methods(['GET', 'POST'])
def pet_create(request):
    """Create shelter pet (shelter owner only)."""
    shelter = _get_shelter_for_user(request.user)
    if not shelter:
        return HttpResponseForbidden('You do not have a shelter.')
    if request.method == 'POST':
        form = ShelterPetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.shelter = shelter
            pet.save()
            if request.FILES.get('image'):
                pet.image = request.FILES['image']
                pet.save(update_fields=['image'])
            messages.success(request, 'Pet added.')
            return redirect('shelters:dashboard')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ShelterPetForm()
    return render(request, 'shelters/pet_form.html', {'form': form, 'pet': None, 'shelter': shelter})


@login_required
@require_http_methods(['GET', 'POST'])
def pet_edit(request, pk):
    """Edit shelter pet (shelter owner only)."""
    pet = get_object_or_404(ShelterPet, pk=pk)
    if pet.shelter.owner_user_id != request.user.id:
        return HttpResponseForbidden('You cannot edit this pet.')
    if request.method == 'POST':
        form = ShelterPetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            if request.FILES.get('image'):
                pet.image = request.FILES['image']
                pet.save(update_fields=['image'])
            messages.success(request, 'Pet updated.')
            return redirect('shelters:dashboard')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ShelterPetForm(instance=pet)
    return render(request, 'shelters/pet_form.html', {'form': form, 'pet': pet, 'shelter': pet.shelter})


@login_required
@require_POST
def pet_delete(request, pk):
    """Delete shelter pet (shelter owner only)."""
    pet = get_object_or_404(ShelterPet, pk=pk)
    if pet.shelter.owner_user_id != request.user.id:
        return HttpResponseForbidden('You cannot delete this pet.')
    pet.delete()
    messages.success(request, 'Pet removed.')
    return redirect('shelters:dashboard')


# CSV import: required columns species, description, intake_date; address OR lat/lng
REQUIRED_CSV_COLUMNS = ['species', 'description', 'intake_date']
OPTIONAL_CSV_COLUMNS = ['external_id', 'name', 'breed', 'color', 'sex', 'intake_location_text', 'address', 'lat', 'lng', 'status']


def _parse_csv_file(uploaded_file):
    """Return (rows_list, encoding_used)."""
    content = uploaded_file.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        encoding = 'utf-8-sig'
    else:
        encoding = 'utf-8'
    try:
        text = content.decode(encoding)
    except UnicodeDecodeError:
        text = content.decode('latin-1')
        encoding = 'latin-1'
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return rows, encoding


def _validate_row(row, index):
    """Return (is_valid, error_message)."""
    for col in REQUIRED_CSV_COLUMNS:
        if not (row.get(col) or '').strip():
            return False, f"Row {index + 1}: missing required column '{col}'"
    # Must have address or (lat and lng)
    address = (row.get('address') or '').strip()
    lat_s = (row.get('lat') or '').strip()
    lng_s = (row.get('lng') or '').strip()
    if not address and not (lat_s and lng_s):
        return False, f"Row {index + 1}: need 'address' or both 'lat' and 'lng'"
    return True, None


def _hash_for_dedup(row):
    """Generate hash for duplicate detection when external_id is missing."""
    key = '|'.join([
        (row.get('species') or '').strip(),
        (row.get('description') or '').strip()[:200],
        (row.get('intake_date') or '').strip(),
        (row.get('name') or '').strip(),
    ])
    return hashlib.md5(key.encode()).hexdigest()


def _geocode_address(address):
    """Call Google Geocoding API; return (lat, lng) or (None, None). Optional when GOOGLE_MAPS_API_KEY is set."""
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '') or ''
    if not api_key or not (address or '').strip():
        return None, None
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.parse.urlencode({
            'address': (address or '').strip() + ', Latvia',
            'key': api_key,
        })
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        if data.get('status') == 'OK' and data.get('results'):
            loc = data['results'][0]['geometry']['location']
            return round(float(loc['lat']), 6), round(float(loc['lng']), 6)
    except Exception:
        pass
    return None, None


@login_required
@require_http_methods(['GET', 'POST'])
def csv_import(request):
    """Upload CSV, validate, preview (first 10), import. Only shelter owner."""
    shelter = _get_shelter_for_user(request.user)
    if not shelter:
        return HttpResponseForbidden('You do not have a shelter.')
    if request.method == 'GET':
        return render(request, 'shelters/csv_import.html', {'shelter': shelter})
    # POST: confirm_import (no file) -> run import from session; else file upload
    if request.POST.get('confirm_import'):
        rows = request.session.get('csv_import_rows', [])
        sid = request.session.get('csv_import_shelter_id')
        if sid != shelter.id or not rows:
            messages.error(request, 'Session expired. Please upload the CSV again.')
            if 'csv_import_rows' in request.session:
                del request.session['csv_import_rows']
                del request.session['csv_import_shelter_id']
            return redirect('shelters:csv_import')
        created = 0
        skipped = 0
        errors = []
        seen_external = set()
        seen_hash = set()
        with transaction.atomic():
            for i, row in enumerate(rows):
                valid, err = _validate_row(row, i)
                if not valid:
                    errors.append(err)
                    skipped += 1
                    continue
                external_id = (row.get('external_id') or '').strip()
                if external_id:
                    if shelter.pets.filter(external_id=external_id).exists() or external_id in seen_external:
                        errors.append(f"Row {i + 1}: duplicate external_id '{external_id}'")
                        skipped += 1
                        continue
                    seen_external.add(external_id)
                if not external_id:
                    h = _hash_for_dedup(row)
                    if h in seen_hash:
                        errors.append(f"Row {i + 1}: duplicate row (same species/description/date/name)")
                        skipped += 1
                        continue
                    seen_hash.add(h)
                pet = ShelterPet(
                    shelter=shelter,
                    external_id=external_id or '',
                    name=(row.get('name') or '').strip(),
                    species=(row.get('species') or '').strip(),
                    breed=(row.get('breed') or '').strip(),
                    color=(row.get('color') or '').strip(),
                    sex=(row.get('sex') or '').strip(),
                    description=(row.get('description') or '').strip(),
                    intake_location_text=(row.get('address') or row.get('intake_location_text') or '').strip(),
                    status=(row.get('status') or ShelterPet.STATUS_IN_CARE).strip() or ShelterPet.STATUS_IN_CARE,
                )
                try:
                    from datetime import datetime
                    d = (row.get('intake_date') or '').strip()
                    if d:
                        pet.intake_date = datetime.strptime(d[:10], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
                lat_s = (row.get('lat') or '').strip()
                lng_s = (row.get('lng') or '').strip()
                if lat_s and lng_s:
                    try:
                        pet.lat = float(lat_s)
                        pet.lng = float(lng_s)
                    except (ValueError, TypeError):
                        pass
                if pet.lat is None and pet.lng is None:
                    addr = (row.get('address') or row.get('intake_location_text') or '').strip()
                    if addr:
                        geo_lat, geo_lng = _geocode_address(addr)
                        if geo_lat is not None and geo_lng is not None:
                            pet.lat = geo_lat
                            pet.lng = geo_lng
                pet.save()
                created += 1
        messages.success(request, f'Import finished: {created} created, {skipped} skipped.')
        if errors:
            for e in errors[:20]:
                messages.warning(request, e)
            if len(errors) > 20:
                messages.warning(request, f'... and {len(errors) - 20} more errors.')
        if 'csv_import_rows' in request.session:
            del request.session['csv_import_rows']
            del request.session['csv_import_shelter_id']
        return redirect('shelters:dashboard')
    # POST: file upload (no confirm_import)
    uploaded = request.FILES.get('csv_file')
    if not uploaded:
        messages.error(request, 'Please select a CSV file.')
        return redirect('shelters:csv_import')
    if not uploaded.name.lower().endswith('.csv'):
        messages.error(request, 'File must be a CSV.')
        return redirect('shelters:csv_import')
    rows, encoding = _parse_csv_file(uploaded)
    if not rows:
        messages.error(request, 'CSV is empty or has no headers.')
        return redirect('shelters:csv_import')
    headers = list(rows[0].keys()) if rows else []
    missing = [c for c in REQUIRED_CSV_COLUMNS if c not in headers]
    if missing:
        messages.error(request, f"CSV must have columns: {', '.join(REQUIRED_CSV_COLUMNS)}. Missing: {', '.join(missing)}.")
        return redirect('shelters:csv_import')
    # Preview: first 10 rows with validation (cells = values in header order for template)
    preview = []
    for i, row in enumerate(rows[:10]):
        valid, err = _validate_row(row, i)
        cells = [row.get(h) for h in headers]
        preview.append({'row': row, 'cells': cells, 'index': i + 1, 'valid': valid, 'error': err})
    # Store rows in session for confirm step (file cannot be re-uploaded)
    request.session['csv_import_rows'] = rows
    request.session['csv_import_shelter_id'] = shelter.id
    return render(request, 'shelters/csv_import.html', {
        'shelter': shelter,
        'preview': preview,
        'total_rows': len(rows),
        'headers': headers,
        'encoding': encoding,
    })
