import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Sotuv, SotuvItem
from mahsulotlar.models import Mahsulot, MahsulotTuri
from hodimlar.models import Hodim


def sotuv_list(request):
    sotuvlar = Sotuv.objects.all().select_related('sotuvchi').prefetch_related('items__mahsulot')
    
    # Statistika
    jami_sotuvlar = sotuvlar.count()
    jami_summa = sotuvlar.aggregate(total=Sum('jami_summa'))['total'] or 0
    
    context = {
        'sotuvlar': sotuvlar,
        'jami_sotuvlar': jami_sotuvlar,
        'jami_summa': jami_summa,
    }
    return render(request, 'sotuv/list.html', context)


def sotuv_detail(request, id):
    sotuv = get_object_or_404(Sotuv.objects.prefetch_related('items__mahsulot'), id=id)
    context = {
        'sotuv': sotuv
    }
    return render(request, 'sotuv/detail.html', context)


@login_required
def receipt_view(request, id):
    """Receipt view with print functionality"""
    sotuv = get_object_or_404(Sotuv.objects.prefetch_related('items__mahsulot', 'sotuvchi'), id=id)
    context = {
        'sotuv': sotuv
    }
    return render(request, 'sotuv/receipt.html', context)


@login_required
def search_by_barcode(request):
    """Search product by barcode"""
    if request.method == 'GET':
        barcode = request.GET.get('barcode', '').strip()
        if not barcode:
            return JsonResponse({'error': 'Barcode kiritilmagan'}, status=400)
        
        try:
            product = Mahsulot.objects.get(barcode=barcode)
            return JsonResponse({
                'status': 'success',
                'product': {
                    'id': product.id,
                    'name': product.nomi,
                    'price': str(product.narx),
                    'stock': product.miqdor,
                    'category': product.turi_id if product.turi else None
                }
            })
        except Mahsulot.DoesNotExist:
            return JsonResponse({'error': 'Bunday barcode bilan mahsulot topilmadi'}, status=404)
        except Mahsulot.MultipleObjectsReturned:
            return JsonResponse({'error': 'Bir nechta mahsulot topildi'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)


@login_required
def pos_view(request):
    products = Mahsulot.objects.all()
    categories = MahsulotTuri.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'sotuv/pos.html', context)


@transaction.atomic
def create_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'error': 'Hech qanday mahsulot tanlanmagan'}, status=400)
            
            # Use logged in user as seller
            try:
                seller = Hodim.objects.get(user=request.user)
            except Hodim.DoesNotExist:
                # Fallback for superuser or if no hodim profile exists
                if request.user.is_superuser:
                    seller = Hodim.objects.first()
                    if not seller:
                         return JsonResponse({'error': 'Tizimda xodimlar mavjud emas'}, status=400)
                else:
                    return JsonResponse({'error': 'Siz xodim sifatida ro\'yxatdan o\'tmagansiz'}, status=403)

            # Create the sale record
            sotuv = Sotuv.objects.create(
                sotuvchi=seller
            )
            
            for item in items:
                mahsulot = get_object_or_404(Mahsulot, id=item['id'])
                miqdor = int(item['quantity'])
                
                if mahsulot.miqdor < miqdor:
                    raise Exception(f"{mahsulot.nomi} uchun yetarli qoldiq yo'q (Mavjud: {mahsulot.miqdor})")
                
                SotuvItem.objects.create(
                    sotuv=sotuv,
                    mahsulot=mahsulot,
                    miqdor=miqdor,
                    narx=mahsulot.narx
                )
            
            # Total is automatically updated in SotuvItem.save()
            
            return JsonResponse({
                'status': 'success',
                'sale_id': sotuv.id,
                'total': sotuv.jami_summa
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)
