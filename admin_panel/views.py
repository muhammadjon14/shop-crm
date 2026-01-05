from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from mahsulotlar.models import Mahsulot, MahsulotTuri
from mahsulotlar.forms import MahsulotForm
from hodimlar.models import Hodim
from hodimlar.forms import HodimForm
from sotuv.models import Sotuv, SotuvItem
from django.contrib import messages

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    
    # Stats
    bugungi_savdo = Sotuv.objects.filter(yaratilgan_vaqt__date=today).aggregate(total=Sum('jami_summa'))['total'] or 0
    jami_mahsulotlar = Mahsulot.objects.count()
    jami_hodimlar = Hodim.objects.count()
    jami_sotuvlar = Sotuv.objects.count()
    
    # Recent sales
    recent_sales = Sotuv.objects.all().order_by('-yaratilgan_vaqt')[:5]
    
    # Low stock products
    low_stock_products = Mahsulot.objects.filter(miqdor__lt=10).order_by('miqdor')[:5]
    
    context = {
        'bugungi_savdo': bugungi_savdo,
        'jami_mahsulotlar': jami_mahsulotlar,
        'jami_hodimlar': jami_hodimlar,
        'jami_sotuvlar': jami_sotuvlar,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'active_tab': 'dashboard'
    }
    return render(request, 'admin_panel/dashboard.html', context)

# Product Management
@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Mahsulot.objects.all().order_by('-yaratilgan_vaqt')
    context = {
        'products': products,
        'active_tab': 'products'
    }
    return render(request, 'admin_panel/products/list.html', context)

@login_required
@user_passes_test(is_admin)
def product_add(request):
    if request.method == 'POST':
        form = MahsulotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot muvaffaqiyatli qo'shildi.")
            return redirect('admin_product_list')
    else:
        form = MahsulotForm()
    
    context = {
        'form': form,
        'title': "Yangi mahsulot qo'shish",
        'active_tab': 'products'
    }
    return render(request, 'admin_panel/products/add_edit.html', context)

@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Mahsulot, pk=pk)
    if request.method == 'POST':
        form = MahsulotForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot muvaffaqiyatli yangilandi.")
            return redirect('admin_product_list')
    else:
        form = MahsulotForm(instance=product)
    
    context = {
        'form': form,
        'title': f"Tahrirlash: {product.nomi}",
        'active_tab': 'products'
    }
    return render(request, 'admin_panel/products/add_edit.html', context)

# Employee Management
@login_required
@user_passes_test(is_admin)
def employee_list(request):
    employees = Hodim.objects.all().order_by('-yaratilgan_vaqt')
    context = {
        'employees': employees,
        'active_tab': 'employees'
    }
    return render(request, 'admin_panel/employees/list.html', context)

@login_required
@user_passes_test(is_admin)
def employee_add(request):
    if request.method == 'POST':
        form = HodimForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Xodim muvaffaqiyatli qo'shildi.")
            return redirect('admin_employee_list')
    else:
        form = HodimForm()
    
    context = {
        'form': form,
        'title': "Yangi xodim qo'shish",
        'active_tab': 'employees'
    }
    return render(request, 'admin_panel/employees/add_edit.html', context)

@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    hodim = get_object_or_404(Hodim, pk=pk)
    if request.method == 'POST':
        form = HodimForm(request.POST, instance=hodim)
        if form.is_valid():
            form.save()
            messages.success(request, "Xodim ma'lumotlari muvaffaqiyatli yangilandi.")
            return redirect('admin_employee_list')
    else:
        form = HodimForm(instance=hodim)
    
    context = {
        'form': form,
        'title': f"Tahrirlash: {hodim.ism} {hodim.familiya}",
        'active_tab': 'employees'
    }
    return render(request, 'admin_panel/employees/add_edit.html', context)

# Sales Management
@login_required
@user_passes_test(is_admin)
def sales_list(request):
    sales = Sotuv.objects.all().order_by('-yaratilgan_vaqt')
    context = {
        'sales': sales,
        'active_tab': 'sales'
    }
    return render(request, 'admin_panel/sales/list.html', context)
