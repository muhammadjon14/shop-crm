from django import forms
from .models import Mahsulot

class MahsulotForm(forms.ModelForm):
    class Meta:
        model = Mahsulot
        fields = '__all__'
