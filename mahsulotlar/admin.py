from django.contrib import admin
from django import forms
from .models import Mahsulot, MahsulotTuri


class MahsulotForm(forms.ModelForm):
    LITRE_OPTIONS = [
        ('0.29', '0.29L'),
        ('0.33', '0.33L'),
        ('0.45', '0.45L'),
        ('0.5', '0.5L'),
        ('0.7', '0.7L'),
        ('1.0', '1L'),
        ('1.5', '1.5L'),
        ('2.0', '2L'),
        ('2.5', '2.5L'),
        ('5.0', '5L'),
    ]
    
    # Use MultipleChoiceField for the UI, but we'll need to save it to the JSONField
    litre_selection = forms.MultipleChoiceField(
        choices=LITRE_OPTIONS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Litrlar'
    )

    class Meta:
        model = Mahsulot
        fields = '__all__'
        exclude = ['litre'] # We'll handle this manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.litre:
            self.initial['litre_selection'] = self.instance.litre

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.litre = self.cleaned_data['litre_selection']
        if commit:
            instance.save()
        return instance


@admin.register(MahsulotTuri)
class MahsulotTuriAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'yaratilgan_vaqt']
    search_fields = ['nomi']
    list_per_page = 20


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    form = MahsulotForm
    list_display = ['nomi', 'turi', 'get_litres', 'narx', 'miqdor', 'yaratilgan_vaqt']
    list_filter = ['turi', 'yaratilgan_vaqt']
    search_fields = ['nomi']
    list_per_page = 20
    date_hierarchy = 'yaratilgan_vaqt'
    
    def get_litres(self, obj):
        return ", ".join(obj.litre) if obj.litre else "-"
    get_litres.short_description = "Litrlar"