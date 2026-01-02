from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/home/', views.api_home, name='api_home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]