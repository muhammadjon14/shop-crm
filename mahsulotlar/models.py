from django.db import models


class MahsulotTuri(models.Model):
    """Mahsulot turlari - alohida sahifadan boshqarish mumkin"""
    nomi = models.CharField(max_length=100, verbose_name='Tur nomi', unique=True)
    tavsif = models.TextField(verbose_name='Tavsif', blank=True)
    icon = models.CharField(max_length=10, verbose_name='Emoji/Icon', blank=True, default='📦')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    class Meta:
        verbose_name = "Mahsulot turi"
        verbose_name_plural = "Mahsulot turlari"
        ordering = ['nomi']

    def __str__(self):
        return f"{self.icon} {self.nomi}" if self.icon else self.nomi


class Mahsulot(models.Model):
    nomi = models.CharField(max_length=200, verbose_name='Mahsulot nomi')
    tavsif = models.TextField(verbose_name='Tavsif', blank=True)
    narx = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Narx')
    miqdor = models.IntegerField(verbose_name='Miqdor', default=0)
    
    # ForeignKey to separate MahsulotTuri model
    turi = models.ForeignKey(
        MahsulotTuri,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Mahsulot turi',
        related_name='mahsulotlar'
    )
    
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    yangilangan_vaqt = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return self.nomi