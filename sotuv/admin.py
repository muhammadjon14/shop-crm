from django.contrib import admin
from .models import Sotuv, SotuvItem


class SotuvItemInline(admin.TabularInline):
    model = SotuvItem
    extra = 1
    autocomplete_fields = ['mahsulot']


@admin.register(Sotuv)
class SotuvAdmin(admin.ModelAdmin):
    list_display = ('id', 'sotuvchi', 'mijoz_ismi', 'jami_summa', 'yaratilgan_vaqt')
    list_filter = ('yaratilgan_vaqt', 'sotuvchi')
    search_fields = ('mijoz_ismi', 'mijoz_telefon', 'sotuvchi__ism')
    readonly_fields = ('jami_summa', 'yaratilgan_vaqt', 'yangilangan_vaqt')
    inlines = [SotuvItemInline]
    
    fieldsets = (
        ('Sotuv ma\'lumotlari', {
            'fields': ('sotuvchi', 'jami_summa')
        }),
        ('Mijoz ma\'lumotlari', {
            'fields': ('mijoz_ismi', 'mijoz_telefon')
        }),
        ('Qo\'shimcha', {
            'fields': ('izoh', 'yaratilgan_vaqt', 'yangilangan_vaqt')
        }),
    )


@admin.register(SotuvItem)
class SotuvItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sotuv', 'mahsulot', 'miqdor', 'narx', 'jami_summa')
    list_filter = ('sotuv__yaratilgan_vaqt',)
    search_fields = ('mahsulot__nomi', 'sotuv__mijoz_ismi')
