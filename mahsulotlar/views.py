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
        (r'(\d+[.,]?\d*)\s*(?:гр|gr)', 'gr'),  # 70гр, 100gr
    ]
    
    for pattern, unit_type in volume_patterns:
        match = re.search(pattern, name_lower, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            try:
                num_value = float(value)
                if unit_type == 'ml':
                    num_value = num_value / 1000  # Convert ml to litres
                elif unit_type == 'gr':
                    # For grams, we don't have a direct conversion to litres in this context,
                    # but we can try to map it if it's common (e.g., 1000g = 1L)
                    num_value = num_value / 1000
                
                # Map to closest available choice
                litre_choices = [0.29, 0.33, 0.45, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 5.0]
                closest = min(litre_choices, key=lambda x: abs(x - num_value))
                
                # Only return if it's reasonably close (e.g., within 10% or 0.1L)
                if abs(closest - num_value) < 0.1:
                    return [str(closest)]
            except ValueError:
                pass
    return []


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
            'кун охирига', 'бугунги сумма', 'сумма возврат', 'вид оплаты', 'наименование товар',
            'расходная накладная', 'наименование товаров', 'цена за 1шт', 'ед.изм', 'количество', 
            'сумма', 'кол-во', 'цена', '№', 'отгруж', 'блок', 'цена за 1бл', 'кол-во в 1 блоке',
            'заказ', 'клиент', 'отпустил', 'принял', 'итог', 'сумма сум'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip lines with ignore keywords
            line_lower = line.lower()
            if any(kw in line_lower for kw in ignore_keywords):
                continue
            
            # Skip lines that look like phone numbers
            if re.search(r'\+?\d{3,}\s*\(?\d{2,}\)?\s*\d{3,}', line):
                continue
            
            # Skip lines that look like headers (e.g., "ЗАКАЗ №", "Клиент:")
            if re.match(r'^(заказ|клиент|адрес|тел|агент|экспедитор)\b', line_lower):
                continue

            # Skip lines that are mostly numbers (totals, dates, etc.)
            if len(re.sub(r'[\d\s.,]', '', line)) < 3:
                continue

            # Clean up the line: remove leading numbers like "1 ", "2. ", etc.
            line = re.sub(r'^\d+[\s.)-]*', '', line)

            # Pattern 1: Table format with columns separated by tabs or multiple spaces
            parts = re.split(r'\t+|\s{2,}', line)
            if len(parts) >= 2:
                # Try to find a sequence of numbers at the end: [Price] [Qty] [Total] or [Qty] [Price] [Total]
                nums = []
                for part in parts:
                    clean = part.replace(' ', '').replace(',', '.')
                    if re.match(r'^\d+(\.\d+)?$', clean):
                        nums.append((float(clean), parts.index(part)))
                
                if len(nums) >= 3:
                    # Check for Price * Qty = Total (or close to it)
                    for i in range(len(nums) - 2):
                        n1, idx1 = nums[i]
                        n2, idx2 = nums[i+1]
                        n3, idx3 = nums[i+2]
                        
                        # Case 1: n1 (price) * n2 (qty) = n3 (total)
                        # Case 2: n2 (price) * n1 (qty) = n3 (total)
                        if abs(n1 * n2 - n3) < max(n3 * 0.05, 1.0):
                            # Found it!
                            price = n1 if n1 > n2 else n2
                            qty = n2 if n1 > n2 else n1
                            
                            # Name is everything before the first numeric part of the triple
                            name_idx = min(idx1, idx2)
                            name = ' '.join(parts[:name_idx]).strip()
                            # Remove trailing units like "шт", "кг"
                            name = re.sub(r'\s+(?:шт|кг|блок|бл|ед\.изм)\s*$', '', name, flags=re.IGNORECASE)
                            
                            if name:
                                litre = extract_volume(name)
                                extracted_products.append({
                                    'nomi': name,
                                    'narx': str(price),
                                    'miqdor': int(qty),
                                    'litre': litre
                                })
                                break
                    else:
                        # Fallback if no triple found but we have numbers
                        pass
                
                if any(p['nomi'] in line for p in extracted_products):
                    continue

                # Fallback to simpler reverse search if triple check failed
                price = None
                qty = None
                for part in reversed(parts):
                    part = part.strip()
                    clean_part = part.replace(' ', '').replace(',', '.')
                    if re.match(r'^\d+(\.\d+)?$', clean_part):
                        num = float(clean_part)
                        if num > 500 and price is None:
                            price = clean_part
                        elif num <= 500 and qty is None:
                            qty = int(num)
                    
                    if price and qty:
                        idx = parts.index(part)
                        name = ' '.join(parts[:idx]).strip()
                        if name:
                            litre = extract_volume(name)
                            extracted_products.append({
                                'nomi': name,
                                'narx': price,
                                'miqdor': qty,
                                'litre': litre
                            })
                            break
                if any(p['nomi'] in line for p in extracted_products):
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
                        litre=p.get('litre', [])
                    )
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f"{created_count} ta yangi mahsulot muvaffaqiyatli qo'shildi.")
            else:
                messages.info(request, "Hech qanday yangi mahsulot qo'shilmadi (ehtimol ular allaqachon mavjud).")
                
            return JsonResponse({'status': 'success', 'created_count': created_count})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
