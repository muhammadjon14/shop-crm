from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from .models import Sotuv


def sotuv_list(request):
    sotuvlar = Sotuv.objects.all().select_related('mahsulot', 'sotuvchi')
    
    # Statistika
    jami_sotuvlar = sotuvlar.count()
    jami_summa = sum([s.jami_summa for s in sotuvlar]) if sotuvlar.exists() else 0
    tasdiqlangan_soni = sotuvlar.filter(holati='tasdiqlangan').count()
    yetkazilgan_soni = sotuvlar.filter(holati='yetkazilgan').count()
    
    context = {
        'sotuvlar': sotuvlar,
        'jami_sotuvlar': jami_sotuvlar,
        'jami_summa': jami_summa,
        'tasdiqlangan_soni': tasdiqlangan_soni,
        'yetkazilgan_soni': yetkazilgan_soni,
    }
    return render(request, 'sotuv/list.html', context)


def sotuv_detail(request, id):
    sotuv = get_object_or_404(Sotuv, id=id)
    context = {
        'sotuv': sotuv
    }
    return render(request, 'sotuv/detail.html', context)
