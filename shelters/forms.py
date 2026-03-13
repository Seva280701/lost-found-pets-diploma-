from django import forms
from .models import Shelter, ShelterPet


class ShelterForm(forms.ModelForm):
    """Shelter profile edit (name, address, contacts, description, lat/lng)."""
    class Meta:
        model = Shelter
        fields = [
            'name', 'description', 'address', 'city', 'region',
            'phone', 'email', 'website', 'lat', 'lng',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'lat': forms.HiddenInput(attrs={'id': 'id_shelter_lat'}),
            'lng': forms.HiddenInput(attrs={'id': 'id_shelter_lng'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lat'].required = False
        self.fields['lng'].required = False


class ShelterPetForm(forms.ModelForm):
    """Create/Edit shelter pet."""
    class Meta:
        model = ShelterPet
        fields = [
            'name', 'species', 'breed', 'color', 'sex', 'description',
            'intake_date', 'intake_location_text', 'lat', 'lng', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'intake_date': forms.DateInput(attrs={'type': 'date'}),
            'lat': forms.HiddenInput(),
            'lng': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lat'].required = False
        self.fields['lng'].required = False
