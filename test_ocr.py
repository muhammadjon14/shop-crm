import re

def extract_volume(name):
    name_lower = name.lower()
    volume_patterns = [
        (r'(\d+[.,]?\d*)\s*[лl](?:\s|$|[иыa-z])', 'litre'),
        (r'(\d+[.,]?\d*)\s*(?:мл|ml)', 'ml'),
        (r'(\d+[.,]?\d*)\s*(?:гр|gr)', 'gr'),
    ]
    for pattern, unit_type in volume_patterns:
        match = re.search(pattern, name_lower, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            try:
                num_value = float(value)
                if unit_type == 'ml':
                    num_value = num_value / 1000
                elif unit_type == 'gr':
                    num_value = num_value / 1000
                litre_choices = [0.29, 0.33, 0.45, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 5.0]
                closest = min(litre_choices, key=lambda x: abs(x - num_value))
                if abs(closest - num_value) < 0.1:
                    return [str(closest)]
            except ValueError:
                pass
    return []

def parse_line(line):
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
    line = line.strip()
    if not line or len(line) < 3: return None
    line_lower = line.lower()
    if any(kw in line_lower for kw in ignore_keywords): return None
    if re.search(r'\+?\d{3,}\s*\(?\d{2,}\)?\s*\d{3,}', line): return None
    if re.match(r'^(заказ|клиент|адрес|тел|агент|экспедитор)\b', line_lower): return None
    if len(re.sub(r'[\d\s.,]', '', line)) < 3: return None
    line = re.sub(r'^\d+[\s.)-]*', '', line)
    parts = re.split(r'\t+|\s{2,}', line)
    extracted = []
    if len(parts) >= 2:
        nums = []
        for part in parts:
            clean = part.replace(' ', '').replace(',', '.')
            if re.match(r'^\d+(\.\d+)?$', clean):
                nums.append((float(clean), parts.index(part)))
        if len(nums) >= 3:
            for i in range(len(nums) - 2):
                n1, idx1 = nums[i]
                n2, idx2 = nums[i+1]
                n3, idx3 = nums[i+2]
                if abs(n1 * n2 - n3) < max(n3 * 0.05, 1.0):
                    price = n1 if n1 > n2 else n2
                    qty = n2 if n1 > n2 else n1
                    name_idx = min(idx1, idx2)
                    name = ' '.join(parts[:name_idx]).strip()
                    name = re.sub(r'\s+(?:шт|кг|блок|бл|ед\.изм)\s*$', '', name, flags=re.IGNORECASE)
                    if name:
                        extracted.append({'nomi': name, 'narx': str(price), 'miqdor': int(qty), 'litre': extract_volume(name)})
                        break
    if not extracted:
        price = None
        qty = None
        for part in reversed(parts):
            clean_part = part.replace(' ', '').replace(',', '.')
            if re.match(r'^\d+(\.\d+)?$', clean_part):
                num = float(clean_part)
                if num > 500 and price is None: price = clean_part
                elif num <= 500 and qty is None: qty = int(num)
            if price and qty:
                idx = parts.index(part)
                name = ' '.join(parts[:idx]).strip()
                if name:
                    extracted.append({'nomi': name, 'narx': price, 'miqdor': qty, 'litre': extract_volume(name)})
                    break
    return extracted

test_lines = [
    "ЗАКАЗ №31114 от 25.11.2025",
    "Клиент: 3314-Bobojono'va Nodira",
    "Тел: +998 (99) 564-08-78",
    "1 Talyp конфета с вишневой ванил сливоч шок 1кг*4шт 1 38 000 38 000",
    "5 Зайчик 8,5% 450гр 5 13 000 65 000",
    "Итог 10 285,000 сум",
    "Отпустил: ___________ Принял: ___________"
]

for line in test_lines:
    print(f"Line: {line}")
    print(f"Result: {parse_line(line)}")
    print("-" * 20)
