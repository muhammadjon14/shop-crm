from django.contrib import admin
from .models import Hodim

@admin.register(Hodim)
class HodimAdmin(admin.ModelAdmin):
    list_display = ['ism', 'familiya', 'maosh', 'telefon']
    list_filter = ['maosh']
    search_fields = ['ism', 'familiya']
    list_per_page = 20
