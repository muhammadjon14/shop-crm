from django import forms
from django.contrib.auth.models import User
from .models import Hodim

class HodimForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput(), label='Parol', required=False)
    email = forms.EmailField(label='Email', required=False)

    class Meta:
        model = Hodim
        fields = ['ism', 'familiya', 'maosh', 'telefon']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].help_text = "Parolni o'zgartirish uchun to'ldiring. Aks holda bo'sh qoldiring."

    def save(self, commit=True):
        hodim = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email')

        if hodim.user:
            user = hodim.user
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            hodim.user = user

        if commit:
            hodim.save()
        return hodim
