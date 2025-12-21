from django.db import models

class Hodim(models.Model):
    ism = models.CharField(max_length=100, verbose_name='Ism')
    familiya = models.CharField(max_length=100, verbose_name='Familiya')
    maosh = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Maosh')
    telefon = models.IntegerField(max_length=20, verbose_name='Telefon')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Hodim"
        verbose_name_plural = "Hodimlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return f"{self.ism} {self.familiya}"