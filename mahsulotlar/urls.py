from django.urls import path
from .views import OCRScanView, BulkCreateProductsView

app_name = 'mahsulotlar'

urlpatterns = [
    path('ocr-scan/', OCRScanView.as_view(), name='ocr_scan'),
    path('bulk-create/', BulkCreateProductsView.as_view(), name='bulk_create'),
]
