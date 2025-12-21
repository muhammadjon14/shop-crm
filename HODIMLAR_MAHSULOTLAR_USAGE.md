# Hodimlar va Mahsulotlar Apps - Foydalanish Qo'llanmasi

Bu qo'llanma `hodimlar` (xodimlar) va `mahsulotlar` (mahsulotlar) Django ilovalaridan qanday foydalanishni tushuntiradi.

## Tarkib

1. [Hodimlar App](#hodimlar-app)
2. [Mahsulotlar App](#mahsulotlar-app)
3. [Umumiy Qadamlar](#umumiy-qadamlar)

---

## Hodimlar App

### Maqsad
`hodimlar` ilovasi xodimlar (employees/staff) ma'lumotlarini boshqarish uchun yaratilgan.

### Hozirgi Holati
Ilova yaratilgan, lekin hali modellar, view'lar va URL konfiguratsiyalari qo'shilmagan.

### Qanday Ishlatish

#### 1. Model Yaratish

`hodimlar/models.py` faylida model yarating:

```python
from django.db import models

class Hodim(models.Model):
    ism = models.CharField(max_length=100, verbose_name='Ism')
    familiya = models.CharField(max_length=100, verbose_name='Familiya')
    lavozim = models.CharField(max_length=100, verbose_name='Lavozim')
    maosh = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Maosh')
    telefon = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='Email', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Hodim"
        verbose_name_plural = "Hodimlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return f"{self.ism} {self.familiya}"
```

#### 2. Admin Panelga Qo'shish

`hodimlar/admin.py` faylida:

```python
from django.contrib import admin
from .models import Hodim

@admin.register(Hodim)
class HodimAdmin(admin.ModelAdmin):
    list_display = ['ism', 'familiya', 'lavozim', 'maosh', 'telefon']
    list_filter = ['lavozim']
    search_fields = ['ism', 'familiya', 'email']
    list_per_page = 20
```

#### 3. View Yaratish

`hodimlar/views.py` faylida:

```python
from django.shortcuts import render
from .models import Hodim

def hodimlar_list(request):
    hodimlar = Hodim.objects.all()
    context = {
        'hodimlar': hodimlar
    }
    return render(request, 'hodimlar/list.html', context)

def hodim_detail(request, id):
    hodim = Hodim.objects.get(id=id)
    context = {
        'hodim': hodim
    }
    return render(request, 'hodimlar/detail.html', context)
```

#### 4. URL Konfiguratsiya

`hodimlar` papkasida `urls.py` faylini yarating:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hodimlar_list, name='hodimlar_list'),
    path('<int:id>/', views.hodim_detail, name='hodim_detail'),
]
```

Keyin `config/urls.py` ga qo'shing:

```python
path('hodimlar/', include('hodimlar.urls')),
```

#### 5. Migration Yaratish va Qo'llash

```bash
python manage.py makemigrations hodimlar
python manage.py migrate hodimlar
```

---

## Mahsulotlar App

### Maqsad
`mahsulotlar` ilovasi mahsulotlar (products) ma'lumotlarini boshqarish uchun yaratilgan.

### Hozirgi Holati
Ilova yaratilgan, lekin hali modellar, view'lar va URL konfiguratsiyalari qo'shilmagan.

### Qanday Ishlatish

#### 1. Model Yaratish

`mahsulotlar/models.py` faylida model yarating:

```python
from django.db import models

class Mahsulot(models.Model):
    nomi = models.CharField(max_length=200, verbose_name='Mahsulot nomi')
    tavsif = models.TextField(verbose_name='Tavsif')
    narx = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Narx')
    miqdor = models.IntegerField(verbose_name='Miqdor', default=0)
    kategoriya = models.CharField(max_length=100, verbose_name='Kategoriya')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return self.nomi
```

#### 2. Admin Panelga Qo'shish

`mahsulotlar/admin.py` faylida:

```python
from django.contrib import admin
from .models import Mahsulot

@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'kategoriya', 'narx', 'miqdor']
    list_filter = ['kategoriya']
    search_fields = ['nomi', 'tavsif']
    list_per_page = 20
```

#### 3. View Yaratish

`mahsulotlar/views.py` faylida:

```python
from django.shortcuts import render
from .models import Mahsulot

def mahsulotlar_list(request):
    mahsulotlar = Mahsulot.objects.all()
    context = {
        'mahsulotlar': mahsulotlar
    }
    return render(request, 'mahsulotlar/list.html', context)

def mahsulot_detail(request, id):
    mahsulot = Mahsulot.objects.get(id=id)
    context = {
        'mahsulot': mahsulot
    }
    return render(request, 'mahsulotlar/detail.html', context)
```

#### 4. URL Konfiguratsiya

`mahsulotlar` papkasida `urls.py` faylini yarating:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mahsulotlar_list, name='mahsulotlar_list'),
    path('<int:id>/', views.mahsulot_detail, name='mahsulot_detail'),
]
```

Keyin `config/urls.py` ga qo'shing:

```python
path('mahsulotlar/', include('mahsulotlar.urls')),
```

#### 5. Migration Yaratish va Qo'llash

```bash
python manage.py makemigrations mahsulotlar
python manage.py migrate mahsulotlar
```

---

## Umumiy Qadamlar

### 1. Ilovalarni Settings'ga Qo'shish

`config/settings.py` faylida `INSTALLED_APPS` ro'yxatida ilovalar allaqachon qo'shilgan:

```python
INSTALLED_APPS = [
    # ...
    'hodimlar.apps.HodimlarConfig',
    'mahsulotlar.apps.MahsulotlarConfig',
    # ...
]
```

### 2. Template Yaratish

Har bir app uchun template papkalarini yarating:

```
templates/
    hodimlar/
        list.html
        detail.html
    mahsulotlar/
        list.html
        detail.html
```

### 3. Admin Panelda Ko'rish

1. Serverni ishga tushiring: `python manage.py runserver`
2. Admin panelga kiring: `http://127.0.0.1:8000/admin/`
3. Yaratilgan modellarni ko'ring va boshqaring

### 4. API Yaratish (Ixtiyoriy)

Agar REST API kerak bo'lsa, Django REST Framework'dan foydalaning:

```bash
pip install djangorestframework
```

Keyin `hodimlar/serializers.py` va `mahsulotlar/serializers.py` fayllarini yarating.

### 5. Test Yozish

Har bir app uchun testlar yozing:

`hodimlar/tests.py` va `mahsulotlar/tests.py` fayllarida:

```python
from django.test import TestCase
from .models import Hodim  # yoki Mahsulot

class HodimModelTest(TestCase):
    def test_hodim_yaratish(self):
        hodim = Hodim.objects.create(
            ism="Test",
            familiya="User",
            lavozim="Developer",
            maosh=1000.00,
            telefon="+998901234567"
        )
        self.assertEqual(str(hodim), "Test User")
```

Testlarni ishga tushirish:

```bash
python manage.py test hodimlar
python manage.py test mahsulotlar
```

---

## Foydali Buyruqlar

```bash
# Migration yaratish
python manage.py makemigrations hodimlar
python manage.py makemigrations mahsulotlar

# Migration qo'llash
python manage.py migrate

# Superuser yaratish (admin uchun)
python manage.py createsuperuser

# Server ishga tushirish
python manage.py runserver

# Shell'ga kirish (test qilish uchun)
python manage.py shell
```

---

## Eslatmalar

- Har bir model o'zgartirilganda migration yaratishni unutmang
- Admin panelda modellarni to'g'ri konfiguratsiya qiling
- URL'lar va view'lar nomlarini to'g'ri tanlang
- Template'larda Django template sintaksisidan foydalaning
- Ma'lumotlar bazasini muntazam backup qiling

---

## Yordam

Agar muammo bo'lsa:
1. Django dokumentatsiyasini tekshiring: https://docs.djangoproject.com/
2. Migration xatolarini tekshiring: `python manage.py showmigrations`
3. Server loglarini ko'rib chiqing

