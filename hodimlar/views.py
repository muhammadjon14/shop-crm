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