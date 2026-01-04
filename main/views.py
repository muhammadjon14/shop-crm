from mahsulotlar.models import Mahsulot
from hodimlar.models import Hodim
from sotuv.models import Sotuv
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone

def home(request):



    mahsulotlar = Mahsulot.objects.all()[:8]
    hodimlar = Hodim.objects.all()[:6]
    
    context = {
        'mahsulotlar': mahsulotlar,
        'hodimlar': hodimlar,
        'mahsulotlar_soni': Mahsulot.objects.count(),
        'hodimlar_soni': Hodim.objects.count(),
    }
    return render(request, 'home.html', context)

@login_required
def dashboard(request):
    # Stats for dashboard
    today = timezone.now().date()
    bugungi_savdo = Sotuv.objects.filter(yaratilgan_vaqt__date=today).aggregate(total=Sum('jami_summa'))['total'] or 0
    mahsulotlar_soni = Mahsulot.objects.count()
    xodimlar_soni = Hodim.objects.count()
    
    context = {
        'bugungi_savdo': bugungi_savdo,
        'mahsulotlar_soni': mahsulotlar_soni,
        'xodimlar_soni': xodimlar_soni,
    }
    return render(request, 'dashboard.html', context)

def api_home(request):
    mahsulotlar = Mahsulot.objects.all()[:8]
    hodimlar = Hodim.objects.all()[:6]
    
    mahsulotlar_data = []
    for m in mahsulotlar:
        data = model_to_dict(m)
        if m.turi:
            data['turi_display'] = m.turi.nomi
            # data['turi_icon'] = m.turi.icon # Removed icon from model
        else:
            data['turi_display'] = 'Noma\'lum'
        mahsulotlar_data.append(data)

    hodimlar_data = []
    for h in hodimlar:
        data = model_to_dict(h)
        hodimlar_data.append(data)

    data = {
        'mahsulotlar': mahsulotlar_data,
        'hodimlar': hodimlar_data,
        'stats': {
            'mahsulotlar_count': Mahsulot.objects.count(),
            'hodimlar_count': Hodim.objects.count(),
        }
    }
    return JsonResponse(data)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')