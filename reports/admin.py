from django.contrib import admin
from .models import PetReport, PetImage, ContactRequest


class PetImageInline(admin.TabularInline):
    model = PetImage
    extra = 0


@admin.register(PetReport)
class PetReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'species', 'status', 'location_text', 'reporter_user', 'created_at')
    list_filter = ('report_type', 'status', 'species')
    search_fields = ('description', 'location_text', 'breed')
    inlines = [PetImageInline]


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('from_email', 'from_name', 'contact_target', 'created_at')
    list_filter = ('created_at', 'to_report', 'to_shelter')

    def contact_target(self, obj):
        if obj.to_report_id:
            return f'Report #{obj.to_report_id}'
        if obj.to_shelter_id:
            return f'Shelter: {obj.to_shelter.name}'
        return '—'
    contact_target.short_description = 'Contact target'
