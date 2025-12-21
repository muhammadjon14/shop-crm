from django.contrib import admin
from .models import Mahsulot, MahsulotTuri


@admin.register(MahsulotTuri)
class MahsulotTuriAdmin(admin.ModelAdmin):
    list_display = ['icon', 'nomi', 'tavsif', 'yaratilgan_vaqt']
    search_fields = ['nomi', 'tavsif']
    list_per_page = 20
    
    fieldsets = (
        ('Tur ma\'lumotlari', {
            'fields': ('nomi', 'icon', 'tavsif')
        }),
    )


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'turi', 'narx', 'miqdor', 'yaratilgan_vaqt']
    list_filter = ['turi', 'yaratilgan_vaqt']
    search_fields = ['nomi', 'tavsif']
    list_per_page = 20
    date_hierarchy = 'yaratilgan_vaqt'
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('nomi', 'turi', 'tavsif')
        }),
        ('Narx va miqdor', {
            'fields': ('narx', 'miqdor')
        }),
        ('Vaqt', {
            'fields': ('yaratilgan_vaqt', 'yangilangan_vaqt'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['yaratilgan_vaqt', 'yangilangan_vaqt']