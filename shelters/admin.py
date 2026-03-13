from django.contrib import admin
from .models import Shelter, ShelterPet


class ShelterPetInline(admin.TabularInline):
    model = ShelterPet
    extra = 0
    fields = ('name', 'species', 'breed', 'status', 'intake_date')


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'verified', 'owner_user', 'created_at')
    list_filter = ('verified', 'city')
    search_fields = ('name', 'city', 'address')
    inlines = [ShelterPetInline]


@admin.register(ShelterPet)
class ShelterPetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'shelter', 'status', 'intake_date')
    list_filter = ('species', 'status', 'shelter')
    search_fields = ('name', 'species', 'description')
