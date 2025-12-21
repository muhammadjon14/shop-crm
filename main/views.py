from mahsulotlar.models import Mahsulot
from hodimlar.models import Hodim
from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict

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

def api_home(request):
    mahsulotlar = Mahsulot.objects.all()[:8]
    hodimlar = Hodim.objects.all()[:6]
    
    mahsulotlar_data = []
    for m in mahsulotlar:
        data = model_to_dict(m)
        if m.turi:
            data['turi_display'] = m.turi.nomi
            data['turi_icon'] = m.turi.icon
        else:
            data['turi_display'] = 'Noma\'lum'
            data['turi_icon'] = '📦'
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