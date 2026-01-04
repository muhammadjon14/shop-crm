from django.urls import path
from . import views

urlpatterns = [
    path('', views.sotuv_list, name='sotuv_list'),
    path('pos/', views.pos_view, name='pos'),
    path('create-sale/', views.create_sale, name='create_sale'),
    path('<int:id>/', views.sotuv_detail, name='sotuv_detail'),
    path('<int:id>/receipt/', views.receipt_view, name='receipt'),
    path('search-barcode/', views.search_by_barcode, name='search_barcode'),
]
