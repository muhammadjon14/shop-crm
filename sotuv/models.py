from django.db import models
from mahsulotlar.models import Mahsulot
from hodimlar.models import Hodim





class Sotuv(models.Model):
    sotuvchi = models.ForeignKey(
        Hodim,
        on_delete=models.CASCADE,
        verbose_name='Sotuvchi',
        related_name='sotuvlar'
    )
    
    jami_summa = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Jami summa', default=0)
    izoh = models.TextField(verbose_name='Izoh', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Sotuv"
        verbose_name_plural = "Sotuvlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return f"Sotuv #{self.id} - {self.yaratilgan_vaqt.strftime('%Y-%m-%d %H:%M')}"

    def update_total(self):
        self.jami_summa = sum(item.jami_summa for item in self.items.all())
        self.save()


class SotuvItem(models.Model):
    sotuv = models.ForeignKey(
        Sotuv,
        on_delete=models.CASCADE,
        verbose_name='Sotuv',
        related_name='items'
    )
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        verbose_name='Mahsulot',
        related_name='sotuv_items'
    )

    miqdor = models.PositiveIntegerField(verbose_name='Miqdor', default=1)
    narx = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Sotuv narxi')
    
    class Meta:
        verbose_name = "Sotuv mahsuloti"
        verbose_name_plural = "Sotuv mahsulotlari"

    def __str__(self):
        return f"{self.mahsulot.nomi} x {self.miqdor}"

    @property
    def jami_summa(self):
        return self.narx * self.miqdor

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Decrease stock
            # Decrease stock
            self.mahsulot.miqdor -= self.miqdor
            self.mahsulot.save()
        self.sotuv.update_total()
