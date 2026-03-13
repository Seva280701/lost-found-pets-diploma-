from django import forms
from .models import PetReport, PetImage, ContactRequest
from shelters.models import Shelter
from .widgets import DatalistInput


class PetReportForm(forms.ModelForm):
    """Create/Edit report. Breed and color: text input with suggestions. lat/lng handled separately (no DecimalField validation)."""
    # lat/lng not in Meta.fields — we add them as CharField and set on instance in save()
    lat = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_lat'}))
    lng = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_lng'}))

    class Meta:
        model = PetReport
        fields = [
            'report_type', 'species', 'breed', 'color', 'size', 'sex',
            'description', 'date_time_reported', 'location_text', 'status',
            'linked_shelter',
        ]
        widgets = {
            'breed': DatalistInput(
                attrs={'placeholder': 'Type or choose from suggestions'},
                datalist_options=[c for c in PetReport.BREED_CHOICES if c[0]],
            ),
            'color': DatalistInput(
                attrs={'placeholder': 'Type or choose from suggestions'},
                datalist_options=[c for c in PetReport.COLOR_CHOICES if c[0]],
            ),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_time_reported': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.fields.pop('status', None)  # new reports start as OPEN
        self.fields['size'].choices = [('', '— Select —')] + list(PetReport.SIZE_CHOICES)
        self.fields['sex'].choices = [('', '— Select —')] + list(PetReport.SEX_CHOICES)
        self.fields['linked_shelter'].queryset = Shelter.objects.all().order_by('name')
        self.fields['linked_shelter'].required = False
        self.fields['linked_shelter'].empty_label = '— None —'
        # Pre-fill lat/lng from instance when editing
        if kwargs.get('instance'):
            inst = kwargs['instance']
            if inst.lat is not None:
                self.fields['lat'].initial = str(inst.lat)
            if inst.lng is not None:
                self.fields['lng'].initial = str(inst.lng)

    def clean_lat(self):
        val = self.cleaned_data.get('lat')
        if not val or (isinstance(val, str) and not val.strip()):
            return None
        try:
            return round(float(val), 6)
        except (TypeError, ValueError):
            return None

    def clean_lng(self):
        val = self.cleaned_data.get('lng')
        if not val or (isinstance(val, str) and not val.strip()):
            return None
        try:
            return round(float(val), 6)
        except (TypeError, ValueError):
            return None

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lat = self.cleaned_data.get('lat')
        obj.lng = self.cleaned_data.get('lng')
        if commit:
            obj.save()
        return obj


class ContactRequestForm(forms.ModelForm):
    """Simple contact form (guest or registered)."""
    class Meta:
        model = ContactRequest
        fields = ['from_name', 'from_email', 'message_text']
        widgets = {'message_text': forms.Textarea(attrs={'rows': 4})}
