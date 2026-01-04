from django.contrib import admin
from .models import Mahsulot, MahsulotTuri
from .forms import MahsulotForm


@admin.register(MahsulotTuri)
class MahsulotTuriAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'yaratilgan_vaqt']
    search_fields = ['nomi']
    list_per_page = 20


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    form = MahsulotForm
    list_display = ['nomi', 'turi', 'barcode', 'narx', 'miqdor', 'yaratilgan_vaqt']
    list_filter = ['turi', 'yaratilgan_vaqt']
    search_fields = ['nomi', 'barcode']
    list_per_page = 20
    date_hierarchy = 'yaratilgan_vaqt'