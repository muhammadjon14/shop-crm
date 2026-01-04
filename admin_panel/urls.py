from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.product_list, name='admin_product_list'),
    path('products/add/', views.product_add, name='admin_product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='admin_product_edit'),
    path('employees/', views.employee_list, name='admin_employee_list'),
    path('sales/', views.sales_list, name='admin_sales_list'),
]
