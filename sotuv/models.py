from django.db import models
from mahsulotlar.models import Mahsulot
from hodimlar.models import Hodim


class SotuvHolati(models.TextChoices):
    KUTILMOQDA = 'kutilmoqda', 'Kutilmoqda'
    TASDIQLANGAN = 'tasdiqlangan', 'Tasdiqlangan'
    YETKAZILGAN = 'yetkazilgan', 'Yetkazilgan'
    BEKOR_QILINGAN = 'bekor_qilingan', 'Bekor qilingan'


class Sotuv(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        verbose_name='Mahsulot',
        related_name='sotuvlar'
    )
    
    sotuvchi = models.ForeignKey(
        Hodim,
        on_delete=models.CASCADE,
        verbose_name='Sotuvchi',
        related_name='sotuvlar'
    )
    
    mijoz_ismi = models.CharField(max_length=200, verbose_name='Mijoz ismi')
    mijoz_telefon = models.CharField(max_length=20, verbose_name='Mijoz telefon')
    miqdor = models.PositiveIntegerField(verbose_name='Sotilgan miqdor', default=1)
    narx = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Sotuv narxi')
    
    holati = models.CharField(
        max_length=50,
        choices=SotuvHolati.choices,
        default=SotuvHolati.KUTILMOQDA,
        verbose_name='Holati'
    )
    
    izoh = models.TextField(verbose_name='Izoh', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Sotuv"
        verbose_name_plural = "Sotuvlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return f"{self.mahsulot.nomi} - {self.mijoz_ismi} ({self.miqdor} dona)"

    @property
    def jami_summa(self):
        return self.narx * self.miqdor
