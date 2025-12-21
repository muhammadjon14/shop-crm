from django.urls import path
from . import views

urlpatterns = [
    path('', views.hodimlar_list, name='hodimlar_list'),
    path('<int:id>/', views.hodim_detail, name='hodim_detail'),
]