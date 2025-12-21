from django.contrib import admin
from .models import Sotuv


@admin.register(Sotuv)
class SotuvAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot', 'sotuvchi', 'mijoz_ismi', 'miqdor', 'narx', 'holati', 'yaratilgan_vaqt')
    list_filter = ('holati', 'yaratilgan_vaqt')
    search_fields = ('mijoz_ismi', 'mijoz_telefon', 'mahsulot__nomi', 'sotuvchi__ism')
    list_editable = ('holati',)
    readonly_fields = ('yaratilgan_vaqt', 'yangilangan_vaqt')
    
    fieldsets = (
        ('Mahsulot ma\'lumotlari', {
            'fields': ('mahsulot', 'sotuvchi', 'miqdor', 'narx')
        }),
        ('Mijoz ma\'lumotlari', {
            'fields': ('mijoz_ismi', 'mijoz_telefon')
        }),
        ('Holat', {
            'fields': ('holati', 'izoh')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('yaratilgan_vaqt', 'yangilangan_vaqt'),
            'classes': ('collapse',)
        }),
    )
