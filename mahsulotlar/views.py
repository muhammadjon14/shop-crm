import json
import re
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from .utils import ocr_scan_image
from .models import Mahsulot, MahsulotTuri
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


def extract_volume(name):
    """Extract volume/size from product name and return litre value"""
    name_lower = name.lower()
    
    # Volume patterns to check
    volume_patterns = [
        (r'(\d+[.,]?\d*)\s*[лl](?:\s|$|[иыa-z])', 'litre'),  # 0.5л, 1l, 1.5 л
        (r'(\d+[.,]?\d*)\s*(?:мл|ml)', 'ml'),  # 250мл, 500ml
    ]
    
    for pattern, unit_type in volume_patterns:
        match = re.search(pattern, name_lower, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            try:
                num_value = float(value)
                if unit_type == 'ml':
                    num_value = num_value / 1000  # Convert ml to litres
                
                # Map to closest available choice
                litre_choices = [0.29, 0.33, 0.45, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 5.0]
                closest = min(litre_choices, key=lambda x: abs(x - num_value))
                return str(closest)
            except ValueError:
                pass
    return 'none'


@method_decorator(staff_member_required, name='dispatch')
class OCRScanView(View):
    def get(self, request):
        return render(request, 'mahsulotlar/ocr_scan.html')

    def post(self, request):
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image uploaded'}, status=400)
        
        image_file = request.FILES['image']
        result = ocr_scan_image(image_file)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        lines = result['text'].split('\n')
        extracted_products = []
        
        # Keywords to ignore (common receipt headers/footers/metadata)
        ignore_keywords = [
            'total', 'итого', 'всего', 'cash', 'change', 'tax', 'subtotal', 'visa', 'mastercard', 
            'card', 'thank', 'date', 'дата', 'time', 'tel', 'тел', 'address', 'адрес', 'receipt', 
            'shop', 'approval', 'code', 'bank', 'terminal', 'merchant', 'auth', 'получатель',
            'инн', 'код', 'агент', 'карзини', 'наличный', 'подпись', 'долг', 'последни', 'расчет',
            'примечан', 'экспедитор', 'поставщик', 'комментари', 'товар отгруж', 'кун бошига',
            'кун охирига', 'бугунги сумма', 'сумма возврат', 'вид оплаты', 'наименование товар'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip lines with ignore keywords
            line_lower = line.lower()
            if any(kw in line_lower for kw in ignore_keywords):
                continue
            
            # Skip lines that are mostly numbers (totals, dates, etc.)
            if len(re.sub(r'[\d\s.,]', '', line)) < 3:
                continue

            # Pattern 1: Table format with columns separated by tabs or multiple spaces
            parts = re.split(r'\t+|\s{2,}', line)
            if len(parts) >= 3:
                name_candidates = []
                price = None
                qty = None
                
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    
                    # Check if it's a price (number with thousands separator)
                    price_match = re.match(r'^(\d[\d\s]*[.,]?\d*)$', part.replace(' ', ''))
                    if price_match:
                        val = part.replace(' ', '').replace(',', '.')
                        try:
                            num = float(val)
                            if num > 100:  # Likely a price
                                if price is None:
                                    price = val
                            elif num <= 100 and qty is None:  # Likely quantity
                                qty = int(num)
                        except ValueError:
                            pass
                    else:
                        # Check if it's a quantity with unit
                        qty_match = re.match(r'^(\d+)\s*(?:шт|блок|бл)?$', part, re.IGNORECASE)
                        if qty_match:
                            qty = int(qty_match.group(1))
                        else:
                            name_candidates.append(part)
                
                if name_candidates and price:
                    name = ' '.join(name_candidates)
                    name = re.sub(r'[:.\\-\\s]+$', '', name)
                    if len(name) > 1:
                        litre = extract_volume(name)
                        extracted_products.append({
                            'nomi': name,
                            'narx': price,
                            'miqdor': qty if qty else 1,
                            'litre': litre
                        })
                        continue

            # Pattern 2: Name ... Qty x Price (e.g., "Coca Cola 6 x 12000")
            qty_price_match = re.search(r'(\d+)\s*[xX*]\s*(\d+[.,]?\d*)\s*$', line)
            if qty_price_match:
                qty = qty_price_match.group(1)
                price = qty_price_match.group(2).replace(',', '.')
                name = line[:qty_price_match.start()].strip()
                name = re.sub(r'[:.\\-\\s]+$', '', name)
                if name:
                    litre = extract_volume(name)
                    extracted_products.append({
                        'nomi': name,
                        'narx': price,
                        'miqdor': qty,
                        'litre': litre
                    })
                    continue

            # Pattern 3: Name ... Price (original logic)
            price_match = re.search(r'(\d+[.,]?\d*)\s*$', line)
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                name_part = line[:price_match.start()].strip()
                
                # Check if there's a quantity before the price
                qty_match = re.search(r'(\d+)\s+$', name_part)
                if qty_match:
                    qty = qty_match.group(1)
                    name = name_part[:qty_match.start()].strip()
                else:
                    qty = 1
                    name = name_part
                
                name = re.sub(r'[:.\\-\\s]+$', '', name)
                if name and len(name) > 1:
                    litre = extract_volume(name)
                    extracted_products.append({
                        'nomi': name,
                        'narx': price_str,
                        'miqdor': qty,
                        'litre': litre
                    })
            else:
                # Fallback: if no price at end, maybe it's "Name Price" separated by multiple spaces
                parts = re.split(r'\s{2,}', line)
                if len(parts) >= 2:
                    name = parts[0].strip()
                    price_part = parts[-1].strip()
                    price_match = re.search(r'(\d+[.,]?\d*)', price_part)
                    if price_match:
                        price_str = price_match.group(0).replace(',', '.')
                        litre = extract_volume(name)
                        extracted_products.append({
                            'nomi': name,
                            'narx': price_str,
                            'miqdor': 1,
                            'litre': litre
                        })

        return JsonResponse({
            'raw_text': result['text'],
            'products': extracted_products
        })


@method_decorator(staff_member_required, name='dispatch')
class BulkCreateProductsView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            products_data = data.get('products', [])
            
            created_count = 0
            for p in products_data:
                # Check if a product with same name, price and quantity was created in the last 5 minutes
                from django.utils import timezone
                from datetime import timedelta
                
                five_minutes_ago = timezone.now() - timedelta(minutes=5)
                exists = Mahsulot.objects.filter(
                    nomi=p['nomi'],
                    narx=p['narx'],
                    miqdor=p['miqdor'],
                    yaratilgan_vaqt__gte=five_minutes_ago
                ).exists()
                
                if not exists:
                    mahsulot = Mahsulot.objects.create(
                        nomi=p['nomi'],
                        narx=p['narx'],
                        miqdor=p['miqdor'],
                        litre=p.get('litre', 'none')
                    )
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f"{created_count} ta yangi mahsulot muvaffaqiyatli qo'shildi.")
            else:
                messages.info(request, "Hech qanday yangi mahsulot qo'shilmadi (ehtimol ular allaqachon mavjud).")
                
            return JsonResponse({'status': 'success', 'created_count': created_count})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
